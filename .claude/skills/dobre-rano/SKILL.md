---
name: dobre-rano
description: Ranný prehľad po slovensky – aktuálny čas, počasie vonku, predpoveď na celý deň a najdôležitejšie správy zo Slovenska a zo sveta. Použi vždy, keď používateľ povie "dobré ráno" / "dobre rano" / "dobré ráno, Claude", alebo zavolá /dobre-rano.
---

# Dobré ráno

Používateľ ťa pozdravil ráno. Odpovedz krátkym, priateľským ranným prehľadom **po slovensky**
v presne tomto poradí:

## 1. Čas
Spusti `python3 .claude/skills/dobre-rano/scripts/rano.py` (z koreňa repozitára).
Skript vypíše aktuálny dátum a čas v Europe/Bratislava a počasie.
Ak skript nefunguje, zisti čas cez `TZ=Europe/Bratislava date`.

Začni napr.: „Dobré ráno! Je pondelok 23. novembra, 7:15.“

## 2. Počasie teraz
Z výstupu skriptu: aktuálna teplota, pocitová teplota, obloha, vietor.
Ak skript nevráti počasie (napr. blokovaná sieť), použi WebSearch
(„počasie Bratislava dnes“) – nikdy si počasie nevymýšľaj; keď ho nezistíš, povedz to.

## 3. Ako bude cez deň
Max/min teplota, pravdepodobnosť zrážok, ako sa počasie zmení
(ráno / poobede / večer). Pridaj jednu praktickú radu
(dáždnik, teplá bunda, poľadovica, krém na opaľovanie…).

## 4. Správy zo Slovenska
Použi WebSearch (mode "standard") na dnešné/včerajšie správy zo Slovenska
(napr. „správy Slovensko dnes“, zdroje ako aktuality.sk, dennikn.sk, sme.sk, tasr.sk).
Vyber 3–4 najdôležitejšie, každú v jednej vete.

## 5. Zo sveta
Ak sa vo svete stalo niečo naozaj zaujímavé alebo dôležité, pridaj 1–3 body.
Ak nič výnimočné, túto časť pokojne vynechaj.

## Štýl
- Celé to má byť krátke – prečítateľné do minúty.
- Bez zbytočných úvodov a záverov; na konci max. jedna krátka veta (napr. „Pekný deň!“).
- Uvádzaj len overené informácie z dnešného vyhľadávania, nie z pamäti.

## Nastavenie mesta
Predvolené mesto je Bratislava. Iné mesto: premenné prostredia
`RANO_MESTO`, `RANO_LAT`, `RANO_LON`, alebo ak používateľ v pozdrave spomenie mesto,
spusti skript s `--mesto "Košice"` (súradnice si skript nájde sám).
