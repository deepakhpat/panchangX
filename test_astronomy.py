import datetime
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

def test():
    ts = load.timescale()
    # de421.bsp is a standard JPL ephemeris covering 1900-2050 (approx 17MB)
    print("Loading ephemeris...")
    eph = load('de421.bsp')
    earth = eph['earth']
    sun = eph['sun']
    moon = eph['moon']

    # Date of Sun entering Ardra Nakshatra: June 22, 2026
    # Let's test at 22:52:00 Local time (17:22:00 UTC)
    t = ts.utc(2026, 6, 22, 17, 22, 0)

    # Geocentric observer position
    e_sun = earth.at(t).observe(sun).apparent()
    e_moon = earth.at(t).observe(moon).apparent()

    # Get ecliptic coordinates
    lat_sun, lon_sun, dist_sun = e_sun.frame_latlon(ecliptic_frame)
    lat_moon, lon_moon, dist_moon = e_moon.frame_latlon(ecliptic_frame)

    print("Sayana (Tropical) Sun Longitude:", lon_sun.degrees)
    print("Sayana (Tropical) Moon Longitude:", lon_moon.degrees)

    # Lahiri Ayanamsa for June 2026 is approx 24.135 degrees (24° 8' 6")
    ayanamsa = 24.135

    # Nirayana (Sidereal) longitudes
    s_sun = (lon_sun.degrees - ayanamsa) % 360
    s_moon = (lon_moon.degrees - ayanamsa) % 360

    print("Nirayana (Sidereal) Sun Longitude:", s_sun)
    print("Nirayana (Sidereal) Moon Longitude:", s_moon)

    # Tithi calculation: (Moon - Sun) % 360 / 12
    diff = (s_moon - s_sun) % 360
    tithi = int(diff // 12) + 1
    
    # Nakshatra calculation: Moon longitude / 13.333333
    nakshatra = int(s_moon // (360 / 27)) + 1
    
    # Sun Nakshatra: Sun longitude / 13.333333
    sun_nak = int(s_sun // (360 / 27)) + 1

    print(f"Calculated Tithi Number: {tithi} (1-15: Shukla, 16-30: Krishna)")
    print(f"Calculated Moon Nakshatra Number: {nakshatra}")
    print(f"Calculated Sun Nakshatra Number: {sun_nak}")

if __name__ == '__main__':
    test()
