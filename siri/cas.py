#!/usr/bin/env python3
"""Vygeneruje 1440 krátkych nahrávok s časom (cas/HHMM.mp3), napr.
"Dobré ráno! Je 7 hodín a 15 minút." Spúšťa sa raz (workflow cas.yml)."""
import asyncio
import os
import sys

import edge_tts

HLAS = "sk-SK-ViktoriaNeural"
SLOVA = {1: "jedna", 2: "dve", 3: "tri", 4: "štyri"}


def veta(h, m):
    if h == 0:
        hod = "Je polnoc" if m == 0 else "Je 0 hodín"
    elif h == 1:
        hod = "Je jedna hodina"
    elif 2 <= h <= 4:
        hod = f"Sú {SLOVA[h]} hodiny"
    else:
        hod = f"Je {h} hodín"
    if m == 0:
        return f"Dobré ráno! {hod}."
    if m == 1:
        mi = "jedna minúta"
    elif 2 <= m <= 4:
        mi = f"{SLOVA[m]} minúty"
    else:
        mi = f"{m} minút"
    return f"Dobré ráno! {hod} a {mi}."


async def main(out):
    os.makedirs(out, exist_ok=True)
    sem = asyncio.Semaphore(8)

    async def jedna(h, m):
        path = os.path.join(out, f"{h:02d}{m:02d}.mp3")
        async with sem:
            for pokus in range(5):
                try:
                    await edge_tts.Communicate(veta(h, m), HLAS, rate="-5%").save(path)
                    return
                except Exception as e:
                    print(f"{h:02d}{m:02d} pokus {pokus}: {e}", file=sys.stderr)
                    await asyncio.sleep(2 ** pokus)
            raise RuntimeError(f"Nepodarilo sa: {h:02d}{m:02d}")

    await asyncio.gather(*(jedna(h, m) for h in range(24) for m in range(60)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ukazka":
        for h, m in [(0, 0), (1, 1), (3, 2), (7, 0), (7, 15), (21, 4), (23, 59)]:
            print(f"{h:02d}{m:02d}: {veta(h, m)}")
    else:
        asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "cas"))
