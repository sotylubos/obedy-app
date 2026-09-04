"""
Obecný (fallback) parser denního menu.

Použije se pro každou restauraci, která nemá v parsers/registry.py
zaregistrovaný vlastní parser. Princip: vezme viditelný text stránky,
projde ho po řádcích a hledá řádky obsahující cenu ve tvaru typickém
pro české restaurace (např. "129 Kč", "129,-", "129 CZK").

Nevýhoda: funguje jen tam, kde je na jednom řádku pohromadě název jídla
i cena (běžné u jednoduchých webů/PDF-jako-text). Nefunguje na menu
vyrenderované jako obrázek, PDF sken, nebo když je cena v jiném sloupci
tabulky než text. Pro takové restaurace je potřeba vlastní parser
(viz parsers/registry.py a příklad v parsers/example_custom.py).
"""

import re
from typing import List

from bs4 import BeautifulSoup

from models import MenuItem

PRICE_RE = re.compile(r"(\d{2,4})\s*(,-|Kč|CZK)", re.IGNORECASE)


def parse(html: str) -> List[MenuItem]:
    soup = BeautifulSoup(html, "html.parser")

    # odstraníme skripty/styly, ať nešahají do textu
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    items: List[MenuItem] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = PRICE_RE.search(line)
        if not match:
            continue
        price = match.group(0).strip()
        name = line[: match.start()].strip(" .:-–|")
        if not name or len(name) < 3:
            continue
        items.append(MenuItem(name=name, price=price))

    return items
