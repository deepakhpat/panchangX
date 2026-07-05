import sys
import datetime
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

sys.stdout.reconfigure(encoding='utf-8')

ts = load.timescale()
eph = load('de421.bsp')
earth = eph['earth']
sun = eph['sun']
moon = eph['moon']

def get_ayanamsa(jd):
    T = (jd - 2451545.0) / 36525.0
    return 23.772 + (50.2785 * T * 100) / 3600.0

def get_coordinates(jd):
    t = ts.ut1_jd(jd)
    e_sun = earth.at(t).observe(sun).apparent()
    e_moon = earth.at(t).observe(moon).apparent()
    _, lon_sun, _ = e_sun.frame_latlon(ecliptic_frame)
    _, lon_moon, _ = e_moon.frame_latlon(ecliptic_frame)
    ayanamsa = get_ayanamsa(jd)
    s_sun = (lon_sun.degrees - ayanamsa) % 360
    s_moon = (lon_moon.degrees - ayanamsa) % 360
    return s_sun, s_moon

def find_amavasya_jd(start_jd, end_jd):
    # Binary search to find the exact JD where (s_moon - s_sun) % 360 crosses 0 (or Tithi 30 ends)
    low = start_jd
    high = end_jd
    for _ in range(40):
        mid = (low + high) / 2.0
        s_sun, s_moon = get_coordinates(mid)
        diff = (s_moon - s_sun) % 360
        # If diff is close to 360 or 0
        if diff > 180:
            diff -= 360
        if diff < 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2.0

MONTH_NAMES = [
    "चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद",
    "अश्विन", "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"
]

def get_lunar_months(year):
    # Let's search for new moons from Dec 1 of previous year to Jan 31 of next year
    start_t = ts.utc(year - 1, 12, 1)
    end_t = ts.utc(year + 1, 2, 1)
    
    jds = []
    # Grid search with 1 day step to find new moons
    step = 1.0
    jd = start_t.ut1
    prev_diff = None
    
    while jd < end_t.ut1:
        s_sun, s_moon = get_coordinates(jd)
        diff = (s_moon - s_sun) % 360
        if prev_diff is not None:
            # Check if it crossed 0 (e.g. from 350 to 10)
            if prev_diff > 300 and diff < 60:
                # Amavasya is between jd - step and jd
                am_jd = find_amavasya_jd(jd - step, jd)
                jds.append(am_jd)
        prev_diff = diff
        jd += step
        
    print(f"Found {len(jds)} New Moons (Amavasyas):")
    amavasyas = []
    for am_jd in jds:
        s_sun, _ = get_coordinates(am_jd)
        dt = ts.ut1_jd(am_jd).utc_datetime() + datetime.timedelta(hours=5, minutes=30)
        
        # Determine Rashi of Sun
        # Mesha starts at 0, Vrishabha at 30, etc.
        rashi_idx = int(s_sun // 30)
        month_name = MONTH_NAMES[rashi_idx]
        
        amavasyas.append({
            "jd": am_jd,
            "datetime_ist": dt,
            "sun_deg": s_sun,
            "month_name": month_name
        })
        print(f"New Moon: {dt.strftime('%Y-%m-%d %H:%M:%S')} IST, Sun: {s_sun:.2f} deg, Month: {month_name}")
        
    return amavasyas

if __name__ == '__main__':
    get_lunar_months(2026)
