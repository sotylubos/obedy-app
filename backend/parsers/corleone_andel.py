"""
Parser pro Corleone Anděl (https://www.corleone.cz/poledni-menu-andel).

Stránka (Wix) obsahuje pro každý všední den sekci ve tvaru:

    PONDĚLÍ 07.09.
    NÁZEV JÍDLA VELKÝMI PÍSMENY (ALERGENY)
    anglický překlad malými písmeny
    XX Kč
    ... (další položky) ...
    ÚTERÝ 08.09.
    ...

Restaurace podává polední menu jen ve všední dny (viz text na stránce),
takže o víkendu appka pro tuhle restauraci správně ukáže "menu se
nepodařilo najít" - žádná sekce pro dnešek na stránce není.
"""

import re
from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

from models import MenuItem

WEEKDAY_NAMES = ["PONDĚLÍ", "ÚTERÝ", "STŘEDA", "ČTVRTEK", "PÁTEK", "SOBOTA", "NEDĚLE"]
DAY_HEADER_RE = re.compile(
    r"^(PONDĚLÍ|ÚTERÝ|STŘEDA|ČTVRTEK|PÁTEK|SOBOTA|NEDĚLE)\b", re.IGNORECASE
)
PRICE_RE = re.compile(r"^(\d{2,4})\s*Kč$", re.IGNORECASE)
ALLERGENS_RE = re.compile(r"\s*\([\d,\s]+\)\s*$")


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
    buffer: List[str] = []  # kandidátní řádky (název, anglický překlad) pro aktuální položku

    for line in lines:
        day_match = DAY_HEADER_RE.match(line)
        if day_match:
            current_day = day_match.group(1).upper()
            items_by_day.setdefault(current_day, [])
            buffer = []
            continue

        if current_day is None:
            continue  # ještě jsme nedorazili k první denní sekci (navigace apod.)

        price_match = PRICE_RE.match(line)
        if price_match:
            if buffer:
                name = ALLERGENS_RE.sub("", buffer[0]).strip()
                items_by_day[current_day].append(
                    MenuItem(name=name, price=f"{price_match.group(1)} Kč")
                )
            buffer = []
            continue

        if len(buffer) < 2:
            buffer.append(line)

    return items_by_day.get(_today_name(), [])
