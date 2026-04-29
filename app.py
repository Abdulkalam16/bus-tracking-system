"""
Nellai Engineering College — Bus Tracking System
Firebase Realtime Database Version
Run: python app.py → http://localhost:5000

Setup:
  1. pip install flask firebase-admin
  2. Download serviceAccountKey.json from Firebase Console
     → Project Settings → Service Accounts → Generate new private key
  3. Replace YOUR-PROJECT-ID below with your Firebase project ID
"""

from flask import Flask, jsonify, request, render_template
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import os

app = Flask(__name__)


KEY_FILE = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')

FIREBASE_DB_URL = 'your db url'


if os.path.exists(KEY_FILE):
    cred = credentials.Certificate(KEY_FILE)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})
    USE_FIREBASE = True
    print("✅ Firebase connected!")
else:
    USE_FIREBASE = False
    print("⚠️  serviceAccountKey.json இல்லை — demo mode இயங்குது")

COLLEGE_LAT = 8.4967
COLLEGE_LNG = 77.6539

# ── Seed Data (first run only) ─────────────────────────────────
def seed_firebase():
    if not USE_FIREBASE:
        return
    ref = firebase_db.reference('buses')
    existing = ref.get()
    if existing:
        return  

    seeds = {
        'NEC-01': {'bus_number':'NEC-01','route_name':'Tirunelveli Town Route',
                   'driver_name':'Murugan A.','driver_phone':'9876541110',
                   'from_stop':'Nellai Engg College','to_stop':'Tirunelveli Junction',
                   'via_stops':'Nanguneri, Valliyoor','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':25,'speed_kmh':0,'passengers':38,
                   'capacity':60,'route_color':'#f97316'},
        'NEC-02': {'bus_number':'NEC-02','route_name':'Palayamkottai Route',
                   'driver_name':'Selvam R.','driver_phone':'9876542221',
                   'from_stop':'Nellai Engg College','to_stop':'Palayamkottai Bus Stand',
                   'via_stops':'Nanguneri, Thisayanvilai','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':30,'speed_kmh':0,'passengers':44,
                   'capacity':60,'route_color':'#3b82f6'},
        'NEC-03': {'bus_number':'NEC-03','route_name':'Valliyoor Route',
                   'driver_name':'Rajan K.','driver_phone':'9876543332',
                   'from_stop':'Nellai Engg College','to_stop':'Valliyoor Town',
                   'via_stops':'Nanguneri, Srivaikuntam','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':15,'speed_kmh':0,'passengers':22,
                   'capacity':50,'route_color':'#10b981'},
        'NEC-04': {'bus_number':'NEC-04','route_name':'Thoothukudi Route',
                   'driver_name':'Dinesh P.','driver_phone':'9876544443',
                   'from_stop':'Nellai Engg College','to_stop':'Thoothukudi Central',
                   'via_stops':'Nanguneri, Srivaikuntam','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':40,'speed_kmh':0,'passengers':51,
                   'capacity':60,'route_color':'#8b5cf6'},
        'NEC-05': {'bus_number':'NEC-05','route_name':'Thisayanvilai Route',
                   'driver_name':'Arun S.','driver_phone':'9876545554',
                   'from_stop':'Nellai Engg College','to_stop':'Thisayanvilai',
                   'via_stops':'Nanguneri, Radhapuram','latitude':8.4967,'longitude':77.6539,
                   'status':'Stopped','eta_minutes':0,'speed_kmh':0,'passengers':0,
                   'capacity':45,'route_color':'#ec4899'},
        'NEC-06': {'bus_number':'NEC-06','route_name':'Radhapuram Route',
                   'driver_name':'Venkat M.','driver_phone':'9876546665',
                   'from_stop':'Nellai Engg College','to_stop':'Radhapuram',
                   'via_stops':'Nanguneri, Mel Kalakadu','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':20,'speed_kmh':0,'passengers':35,
                   'capacity':55,'route_color':'#06b6d4'},
        'NEC-07': {'bus_number':'NEC-07','route_name':'Ambasamudram Route',
                   'driver_name':'Karthik L.','driver_phone':'9876547776',
                   'from_stop':'Nellai Engg College','to_stop':'Ambasamudram',
                   'via_stops':'Nanguneri, Cheranmahadevi','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':35,'speed_kmh':0,'passengers':28,
                   'capacity':60,'route_color':'#eab308'},
        'NEC-08': {'bus_number':'NEC-08','route_name':'Srivaikuntam Route',
                   'driver_name':'Prakash N.','driver_phone':'9876548887',
                   'from_stop':'Nellai Engg College','to_stop':'Srivaikuntam',
                   'via_stops':'Nanguneri, Ottapidaram','latitude':8.4967,'longitude':77.6539,
                   'status':'Running','eta_minutes':18,'speed_kmh':0,'passengers':41,
                   'capacity':60,'route_color':'#ef4444'},
    }
    ref.set(seeds)
    print("✅ Firebase seed data added!")

# ── Pages ──────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# ── API: Get all buses ─────────────────────────────────────────
@app.route('/api/buses')
def get_buses():
    q = request.args.get('search', '').strip().lower()
    if USE_FIREBASE:
        data = firebase_db.reference('buses').get() or {}
        buses = list(data.values())
        # Add numeric id for frontend compatibility
        for i, b in enumerate(buses):
            b.setdefault('id', b.get('bus_number', str(i)))
    else:
        buses = _demo_buses()

    if q:
        buses = [b for b in buses if q in (
            (b.get('bus_number','') + b.get('route_name','') +
             b.get('driver_name','') + b.get('from_stop','') +
             b.get('to_stop','')).lower()
        )]
    return jsonify(buses)

# ── API: Get one bus ───────────────────────────────────────────
@app.route('/api/buses/<bus_id>')
def get_bus(bus_id):
    if USE_FIREBASE:
        data = firebase_db.reference(f'buses/{bus_id}').get()
        if data:
            data['id'] = data.get('bus_number', bus_id)
            return jsonify(data)
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'error': 'Demo mode'}), 404

# ── API: Stats ────────────────────────────────────────────────
@app.route('/api/stats')
def stats():
    if USE_FIREBASE:
        data = firebase_db.reference('buses').get() or {}
        buses = list(data.values())
    else:
        buses = _demo_buses()

    total   = len(buses)
    running = sum(1 for b in buses if b.get('status') == 'Running')
    pax     = sum(b.get('passengers', 0) for b in buses)
    return jsonify({'total': total, 'running': running,
                    'stopped': total - running, 'passengers': pax})

# ── API: Add bus (Admin) ───────────────────────────────────────
@app.route('/api/add_bus', methods=['POST'])
def add_bus():
    d = request.get_json()
    if not all(k in d for k in ['bus_number', 'route_name', 'driver_name']):
        return jsonify({'error': 'bus_number, route_name, driver_name required'}), 400

    bus_id = d['bus_number']
    bus_data = {
        'bus_number':   bus_id,
        'route_name':   d['route_name'],
        'driver_name':  d['driver_name'],
        'driver_phone': d.get('driver_phone', ''),
        'from_stop':    d.get('from_stop', 'Nellai Engg College'),
        'to_stop':      d.get('to_stop', ''),
        'via_stops':    d.get('via_stops', ''),
        'latitude':     float(d.get('latitude', COLLEGE_LAT)),
        'longitude':    float(d.get('longitude', COLLEGE_LNG)),
        'status':       d.get('status', 'Running'),
        'eta_minutes':  int(d.get('eta_minutes', 0)),
        'route_color':  d.get('route_color', '#f97316'),
        'passengers':   int(d.get('passengers', 0)),
        'capacity':     int(d.get('capacity', 60)),
        'speed_kmh':    0,
    }

    if USE_FIREBASE:
        existing = firebase_db.reference(f'buses/{bus_id}').get()
        if existing:
            return jsonify({'error': 'Bus number already exists'}), 409
        firebase_db.reference(f'buses/{bus_id}').set(bus_data)
    return jsonify({'success': True})

# ── API: Update location (ESP32 calls this) ────────────────────
@app.route('/api/update_location', methods=['POST'])
def update_location():
    d = request.get_json()
    if not all(k in d for k in ['bus_id', 'latitude', 'longitude']):
        return jsonify({'error': 'bus_id, latitude, longitude required'}), 400

    bus_id = d['bus_id']
    update = {
        'latitude':    float(d['latitude']),
        'longitude':   float(d['longitude']),
        'status':      d.get('status', 'Running'),
        'eta_minutes': int(d.get('eta_minutes', 0)),
        'speed_kmh':   float(d.get('speed_kmh', 0)),
        'passengers':  int(d.get('passengers', 0)),
    }

    if USE_FIREBASE:
        # bus_id can be "NEC-01" or numeric string
        ref = firebase_db.reference(f'buses/{bus_id}')
        if not ref.get():
            # Try by bus_number field if numeric id passed
            all_buses = firebase_db.reference('buses').get() or {}
            for key, val in all_buses.items():
                if str(val.get('id')) == str(bus_id):
                    firebase_db.reference(f'buses/{key}').update(update)
                    return jsonify({'success': True})
        else:
            ref.update(update)
    return jsonify({'success': True})

# ── API: Delete bus (Admin) ────────────────────────────────────
@app.route('/api/delete_bus/<bus_id>', methods=['DELETE'])
def delete_bus(bus_id):
    if USE_FIREBASE:
        firebase_db.reference(f'buses/{bus_id}').delete()
    return jsonify({'success': True})

# ── Demo buses (no Firebase) ───────────────────────────────────
def _demo_buses():
    return [
        {'id':'NEC-01','bus_number':'NEC-01','route_name':'Tirunelveli Town Route',
         'driver_name':'Murugan A.','driver_phone':'9876541110',
         'from_stop':'Nellai Engg College','to_stop':'Tirunelveli Junction',
         'via_stops':'Nanguneri, Valliyoor','latitude':8.52,'longitude':77.70,
         'status':'Running','eta_minutes':25,'speed_kmh':42,'passengers':38,
         'capacity':60,'route_color':'#f97316'},
        {'id':'NEC-02','bus_number':'NEC-02','route_name':'Palayamkottai Route',
         'driver_name':'Selvam R.','driver_phone':'9876542221',
         'from_stop':'Nellai Engg College','to_stop':'Palayamkottai Bus Stand',
         'via_stops':'Nanguneri, Thisayanvilai','latitude':8.49,'longitude':77.68,
         'status':'Running','eta_minutes':30,'speed_kmh':35,'passengers':44,
         'capacity':60,'route_color':'#3b82f6'},
    ]

if __name__ == '__main__':
    if USE_FIREBASE:
        seed_firebase()
    print("\n🚌 Nellai Engineering College — Bus Tracking (Firebase Edition)")
    print(f"   Firebase: {'✅ Connected' if USE_FIREBASE else '⚠️  Demo Mode (add serviceAccountKey.json)'}")
    print("   Home  → http://localhost:5000")
    print("   Admin → http://localhost:5000/admin\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
