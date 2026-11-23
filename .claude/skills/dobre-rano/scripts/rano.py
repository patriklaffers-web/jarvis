#!/usr/bin/env python3
"""Ranný prehľad: aktuálny čas a počasie (Open-Meteo, bez API kľúča)."""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = "Europe/Bratislava"
DNI = ["pondelok", "utorok", "streda", "štvrtok", "piatok", "sobota", "nedeľa"]
MESIACE = ["januára", "februára", "marca", "apríla", "mája", "júna", "júla",
           "augusta", "septembra", "októbra", "novembra", "decembra"]
KODY = {
    0: "jasno", 1: "prevažne jasno", 2: "polojasno", 3: "zamračené",
    45: "hmla", 48: "hmla s námrazou",
    51: "slabé mrholenie", 53: "mrholenie", 55: "silné mrholenie",
    56: "mrznúce mrholenie", 57: "silné mrznúce mrholenie",
    61: "slabý dážď", 63: "dážď", 65: "silný dážď",
    66: "mrznúci dážď", 67: "silný mrznúci dážď",
    71: "slabé sneženie", 73: "sneženie", 75: "silné sneženie", 77: "snehové zrná",
    80: "slabé prehánky", 81: "prehánky", 82: "silné prehánky",
    85: "snehové prehánky", 86: "silné snehové prehánky",
    95: "búrka", 96: "búrka s krupobitím", 99: "silná búrka s krupobitím",
}


def get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def najdi_mesto(nazov):
    q = urllib.parse.urlencode({"name": nazov, "count": 1, "language": "sk"})
    res = get(f"https://geocoding-api.open-meteo.com/v1/search?{q}").get("results")
    if not res:
        raise ValueError(f"Mesto '{nazov}' som nenašiel")
    return res[0]["latitude"], res[0]["longitude"], res[0]["name"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mesto", default=os.environ.get("RANO_MESTO", "Bratislava"))
    a = p.parse_args()

    now = datetime.now(ZoneInfo(TZ))
    print(f"ČAS: {DNI[now.weekday()]} {now.day}. {MESIACE[now.month - 1]} {now.year}, "
          f"{now:%H:%M} ({TZ})")

    try:
        if os.environ.get("RANO_LAT") and os.environ.get("RANO_LON"):
            lat, lon, mesto = float(os.environ["RANO_LAT"]), float(os.environ["RANO_LON"]), a.mesto
        else:
            lat, lon, mesto = najdi_mesto(a.mesto)
        q = urllib.parse.urlencode({
            "latitude": lat, "longitude": lon, "timezone": TZ, "forecast_days": 1,
            "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
            "hourly": "temperature_2m,weather_code,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                     "precipitation_sum,sunrise,sunset,weather_code",
        })
        d = get(f"https://api.open-meteo.com/v1/forecast?{q}")
    except Exception as e:  # sieť zablokovaná a pod.
        print(f"POČASIE: nedostupné ({e}) – použi WebSearch")
        return 0

    c, dy, h = d["current"], d["daily"], d["hourly"]
    print(f"\nPOČASIE TERAZ ({mesto}): {c['temperature_2m']:.0f} °C, "
          f"pocitovo {c['apparent_temperature']:.0f} °C, {KODY.get(c['weather_code'], '?')}, "
          f"vietor {c['wind_speed_10m']:.0f} km/h")
    print(f"\nDNES: {dy['temperature_2m_min'][0]:.0f} až {dy['temperature_2m_max'][0]:.0f} °C, "
          f"{KODY.get(dy['weather_code'][0], '?')}, zrážky {dy['precipitation_probability_max'][0]} % "
          f"({dy['precipitation_sum'][0]} mm), východ {dy['sunrise'][0][-5:]}, "
          f"západ {dy['sunset'][0][-5:]}")
    print("\nPRIEBEH DŇA:")
    for i, t in enumerate(h["time"]):
        hod = int(t[-5:-3])
        if hod in (6, 9, 12, 15, 18, 21):
            print(f"  {t[-5:]}  {h['temperature_2m'][i]:>4.0f} °C  "
                  f"{KODY.get(h['weather_code'][i], '?'):<22} zrážky {h['precipitation_probability'][i]} %")
    return 0


if __name__ == "__main__":
    sys.exit(main())
