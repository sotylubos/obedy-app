"""
Registr parserů menu.

Jakmile pro konkrétní restauraci napíšeme vlastní parser (protože obecná
heuristika na jejím webu nefunguje spolehlivě), přidáme ho jako nový soubor
v tomto adresáři a zaregistrujeme tady pod nějakým jménem. To jméno se pak
použije v restaurants.py u dané restaurace v poli "parser".

Příklad:
    # parsers/u_modre_kachny.py
    def parse(html: str) -> list[MenuItem]:
        ...

    # parsers/registry.py
    from . import u_modre_kachny
    PARSERS["u-modre-kachny"] = u_modre_kachny.parse
"""

from . import generic, corleone_andel, le_camille

PARSERS = {
    "generic": generic.parse,
    "corleone-andel": corleone_andel.parse,
    "le-camille": le_camille.parse,
    # sem přibudou další vlastní parsery pro konkrétní restaurace
}


def get_parser(name: str):
    return PARSERS.get(name, generic.parse)
