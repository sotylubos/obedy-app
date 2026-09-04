"""
Parser pro Le Camille (https://www.lecamille.cz/menu-tydenni).

Stránka (Wix) je jedna týdenní nabídka rozdělená po dnech (PONDĚLÍ..NEDĚLE),
uvnitř po kategoriích (Polévky, Pasta, Risotto, Protein bowl, Specialita
dne). Cena bývá buď na stejném řádku jako název jídla:

    Zeleninová s kari a koriandrem 70 Kč

nebo se stránka zalomí a cena skončí na samostatném řádku:

    Pasta al Pesto di Peperoni Arrostiti (pesto z pečených paprik, ...)
    180 Kč

Parser počítá s oběma variantami.
"""

import re
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from models import MenuItem

WEEKDAY_NAMES = ["PONDĚLÍ", "ÚTERÝ", "STŘEDA", "ČTVRTEK", "PÁTEK", "SOBOTA", "NEDĚLE"]
CATEGORY_LINES = {"polévky", "pasta", "risotto", "protein bowl", "specialita dne"}
PRICE_ONLY_RE = re.compile(r"^(\d{2,4})\s*Kč$", re.IGNORECASE)
PRICE_INLINE_RE = re.compile(r"^(.*\S)\s+(\d{2,4})\s*Kč$", re.IGNORECASE)


def _today_name() -> str:
    today = datetime.now(ZoneInfo("Europe/Prague")).date()
    return WEEKDAY_NAMES[today.weekday()]


def parse(html: str) -> List[MenuItem]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    lines = [l.strip() for l in soup.get_text(separator="\n").splitlines() if l.strip()]

    items_by_day = {}
    current_day = None
    pending_name = None  # jméno jídla čekající na cenu, pokud je na dalším řádku

    for line in lines:
        upper = line.upper()
        if upper in WEEKDAY_NAMES:
            current_day = upper
            items_by_day.setdefault(current_day, [])
            pending_name = None
            continue

        if current_day is None:
            continue

        if line.lower() in CATEGORY_LINES:
            pending_name = None
            continue

        price_only = PRICE_ONLY_RE.match(line)
        if price_only and pending_name:
            items_by_day[current_day].append(
                MenuItem(name=pending_name, price=f"{price_only.group(1)} Kč")
            )
            pending_name = None
            continue

        inline = PRICE_INLINE_RE.match(line)
        if inline:
            items_by_day[current_day].append(
                MenuItem(name=inline.group(1).strip(), price=f"{inline.group(2)} Kč")
            )
            pending_name = None
            continue

        # řádek bez ceny = (začátek) názvu jídla, čeká na cenu na dalším řádku
        pending_name = line

    return items_by_day.get(_today_name(), [])
