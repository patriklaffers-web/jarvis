#!/usr/bin/env python3
"""Vygeneruje ranný prehľad ako text na čítanie nahlas (pre Siri skratku).

Výstup: počasie v Banskej Bystrici + hlavné správy zo Slovenska a sveta.
Čas nepridáva – ten dopĺňa skratka v iPhone (aby bol vždy aktuálny).
"""
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

MESTO = "Banská Bystrica"
LAT, LON = 48.7363, 19.1462
TZ = "Europe/Bratislava"
RSS = "https://news.google.com/rss?hl=sk&gl=SK&ceid=SK:sk"
POCET_SPRAV = 5

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


def stupne(t):
    n = round(t)
    a = abs(n)
    slovo = "stupeň" if a == 1 else "stupne" if 2 <= a <= 4 else "stupňov"
    return f"{'mínus ' if n < 0 else ''}{a} {slovo}"


def cislo(t):
    n = round(t)
    return f"{'mínus ' if n < 0 else ''}{abs(n)}"


def stiahni(url):
    req = urllib.request.Request(url, headers={"User-Agent": "jarvis-rano/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def pocasie():
    q = urllib.parse.urlencode({
        "latitude": LAT, "longitude": LON, "timezone": TZ, "forecast_days": 1,
        "current": "temperature_2m,apparent_temperature,weather_code",
        "hourly": "temperature_2m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
    })
    d = json.loads(stiahni(f"https://api.open-meteo.com/v1/forecast?{q}"))
    c, dy, h = d["current"], d["daily"], d["hourly"]
    zrazky = dy["precipitation_probability_max"][0] or 0
    tmin, tmax = dy["temperature_2m_min"][0], dy["temperature_2m_max"][0]
    vety = [
        f"V Banskej Bystrici je teraz {stupne(c['temperature_2m'])}, "
        f"{KODY.get(c['weather_code'], 'neznáme počasie')}, "
        f"pocitovo {stupne(c['apparent_temperature'])}.",
        f"Cez deň bude od {cislo(tmin)} do {cislo(tmax)} "
        f"{'stupňa' if abs(round(tmax)) == 1 else 'stupňov'}, "
        f"{KODY.get(dy['weather_code'][0], '')}, šanca na zrážky {zrazky} percent.",
    ]
    casti = []
    for nazov, hod in (("doobeda", 10), ("poobede", 15), ("večer", 19)):
        casti.append(f"{nazov} {stupne(h['temperature_2m'][hod])} a "
                     f"{KODY.get(h['weather_code'][hod], '')}")
    vety.append(", ".join(casti).capitalize() + ".")
    rady = []
    sneh = dy["weather_code"][0] in (71, 73, 75, 77, 85, 86)
    if zrazky >= 50 and not sneh:
        rady.append("zober si dáždnik")
    if tmin <= 0:
        rady.append("pozor na poľadovicu" if zrazky >= 30 else "obleč sa teplo")
    elif tmax >= 28:
        rady.append("pi veľa vody")
    if rady:
        vety.append(" a ".join(rady).capitalize() + ".")
    return " ".join(vety)


def spravy():
    root = ET.fromstring(stiahni(RSS))
    tituly = []
    for item in root.iter("item"):
        t = item.findtext("title") or ""
        t = re.sub(r"\s+[-–]\s+[^-–]+$", "", t).strip()  # odstráň " - Zdroj"
        if t and t not in tituly:
            tituly.append(t.rstrip(".!?") + ".")
        if len(tituly) >= POCET_SPRAV:
            break
    return "Zo správ: " + " ".join(tituly) if tituly else ""


def main():
    casti = []
    for f in (pocasie, spravy):
        try:
            casti.append(f())
        except Exception as e:
            print(f"Chyba v {f.__name__}: {e}", file=sys.stderr)
    casti.append("Pekný deň!")
    print(" ".join(c for c in casti if c))


if __name__ == "__main__":
    main()
