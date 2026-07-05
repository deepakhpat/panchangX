import datetime
import numpy as np
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

# Load timescale and ephemeris
ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']

# Monsoon Nakshatras (indices 1-indexed, starting from Ashwini = 1)
MONSOON_NAKSHATRAS = [
    {"id": 4, "name": "Rohini", "marathi_name": "रोहिणी", "start_deg": 40.0},
    {"id": 5, "name": "Mriga", "marathi_name": "मृग", "start_deg": 53.333333},
    {"id": 6, "name": "Ardra", "marathi_name": "आर्द्रा", "start_deg": 66.666667},
    {"id": 7, "name": "Punarvasu", "marathi_name": "पुनर्वसू", "start_deg": 80.0},
    {"id": 8, "name": "Pushya", "marathi_name": "पुष्य", "start_deg": 93.333333},
    {"id": 9, "name": "Ashlesha", "marathi_name": "आश्लेषा", "start_deg": 106.666667},
    {"id": 10, "name": "Magha", "marathi_name": "मघा", "start_deg": 120.0},
    {"id": 11, "name": "Purva Phalguni", "marathi_name": "पूर्वा", "start_deg": 133.333333},
    {"id": 12, "name": "Uttara Phalguni", "marathi_name": "उत्तरा", "start_deg": 146.666667},
    {"id": 13, "name": "Hasta", "marathi_name": "हस्त", "start_deg": 160.0},
    {"id": 14, "name": "Chitra", "marathi_name": "चित्रा", "start_deg": 173.333333},
    {"id": 15, "name": "Swati", "marathi_name": "स्वाती", "start_deg": 186.666667},
    {"id": 16, "name": "Vishakha", "marathi_name": "विशाखा", "start_deg": 200.0}
]

VAHANS = {
    1: {"name": "Horse", "marathi": "घोडा", "rain": "Medium (मध्यम पाऊस)"},
    2: {"name": "Fox", "marathi": "कोल्हा", "rain": "Low/Uneven (कमी किंवा ओढ देणारा पाऊस)"},
    3: {"name": "Frog", "marathi": "बेडूक", "rain": "Very Good (उत्तम पाऊस)"},
    4: {"name": "Ram", "marathi": "मेंढा", "rain": "Low/Uneven (कमी किंवा ओढ देणारा पाऊस)"},
    5: {"name": "Peacock", "marathi": "मोर", "rain": "Medium (मध्यम पाऊस)"},
    6: {"name": "Mouse", "marathi": "उंदीर", "rain": "Low/Crop damage (अल्प पाऊस / उंदरांचा प्रादुर्भाव)"},
    7: {"name": "Buffalo", "marathi": "म्हैस", "rain": "Heavy (भरपूर पाऊस)"},
    8: {"name": "Donkey", "marathi": "गाढव", "rain": "Scant/Dry (अल्प पाऊस / कोरडे हवामान)"},
    0: {"name": "Elephant", "marathi": "हत्ती", "rain": "Very Heavy (मुसळधार पाऊस)"}
}

# Ayanamsa formula: Lahiri Ayanamsa approximation adjusted for mid-2026
def get_ayanamsa(jd):
    T = (jd - 2451545.0) / 36525.0
    # Refined offset to match exactly June 2026 = 24.135 degrees
    return 23.772 + (50.2785 * T * 100) / 3600.0

def get_nirayana_longitudes(jd):
    t = ts.ut1_jd(jd)
    e_sun = earth.at(t).observe(sun).apparent()
    e_moon = earth.at(t).observe(moon).apparent()
    _, lon_sun, _ = e_sun.frame_latlon(ecliptic_frame)
    _, lon_moon, _ = e_moon.frame_latlon(ecliptic_frame)
    
    ayanamsa = get_ayanamsa(jd)
    
    s_sun = (lon_sun.degrees - ayanamsa) % 360
    s_moon = (lon_moon.degrees - ayanamsa) % 360
    return s_sun, s_moon

def find_ingress_jd(year, nak_start_deg, start_jd_est, end_jd_est):
    # Pure Python bisection search for monotonic Sun longitude
    low = start_jd_est
    high = end_jd_est
    for _ in range(50):  # 50 iterations gives sub-millisecond precision
        mid = (low + high) / 2.0
        s_sun, _ = get_nirayana_longitudes(mid)
        # Compute difference, accounting for 360 deg wrap-around
        diff = (s_sun - nak_start_deg + 180) % 360 - 180
        if diff < 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

def calculate_year_vahans(year):
    print(f"\n--- Calculations for Year {year} ---")
    results = []
    
    # Approx JD bounds for the monsoon months (May 15 to Nov 20)
    t_start = ts.utc(year, 5, 15)
    current_est_jd = t_start.ut1
    
    for nak in MONSOON_NAKSHATRAS:
        # Search window of 25 days
        s_jd = current_est_jd
        e_jd = s_jd + 25.0
        
        ingress_jd = find_ingress_jd(year, nak["start_deg"], s_jd, e_jd)
        current_est_jd = ingress_jd  # update for next search
        
        # Get Sun and Moon positions at the exact moment of ingress
        s_sun, s_moon = get_nirayana_longitudes(ingress_jd)
        
        # Convert JD to datetime
        dt = ts.ut1_jd(ingress_jd).utc_datetime()
        
        # Calculate Moon Nakshatra at that moment
        moon_nak_idx = int(s_moon // (360.0 / 27.0)) + 1
        
        # Count from Sun Nakshatra (nak["id"]) to Moon Nakshatra (moon_nak_idx)
        count = (moon_nak_idx - nak["id"]) % 27 + 1
        
        # Vahan index is count % 9
        vahan_idx = count % 9
        vahan_data = VAHANS[vahan_idx]
        
        # Convert to IST (UTC + 5:30)
        ist_dt = dt + datetime.timedelta(hours=5, minutes=30)
        
        results.append({
            "nak_id": nak["id"],
            "name": nak["name"],
            "marathi_name": nak["marathi_name"],
            "ingress_time_utc": dt.strftime('%Y-%m-%d %H:%M:%S'),
            "ingress_time_ist": ist_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "moon_nak": moon_nak_idx,
            "vahan_id": vahan_idx,
            "vahan_name": vahan_data["name"],
            "vahan_marathi": vahan_data["marathi"],
            "rain_forecast": vahan_data["rain"]
        })
        
        print(f"Sun Ingress into {nak['name']} ({nak['marathi_name']}):")
        print(f"  Date & Time (IST): {ist_dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Moon Nakshatra Index: {moon_nak_idx}")
        print(f"  Count (Moon - Sun + 1): {count}")
        print(f"  Calculated Vahan: {vahan_data['marathi']} ({vahan_data['name']}) -> {vahan_data['rain']}")
        print("-" * 50)
        
    return results

if __name__ == '__main__':
    calculate_year_vahans(2026)
