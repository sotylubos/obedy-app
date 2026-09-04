"""
Seznam restaurací, které appka sleduje.

Až mi pošleš konkrétní restaurace a odkazy na jejich stránku s denním menu,
doplním je sem a pro každou napíšu přesný parser podle skutečné struktury
jejího webu (viz backend/parsers/).

Formát jedné položky:
{
    "id": "unikatni-identifikator",     # bez diakritiky a mezer, použije se v URL a hlasování
    "name": "Zobrazovaný název",
    "menu_url": "https://...",          # stránka, kde restaurace zveřejňuje denní menu
    "address": "Ulice 123, Praha",      # volitelné
    "parser": "generic",                # "generic" = heuristika níže, nebo jméno vlastního parseru
}

Pokud pro restauraci není zaregistrovaný vlastní parser (viz parsers/registry.py),
použije se obecná heuristika (parsers/generic.py), která z textu stránky hledá
řádky s cenou (např. "Svíčková na smetaně ... 159 Kč"). Funguje překvapivě
dobře na jednoduché weby, ale u složitějších (např. menu jako obrázek, PDF,
nebo JS aplikace) bude potřeba napsat vlastní parser na míru.
Formát jedné položky:
{
    "id": "unikatni-identifikator",     # bez diakritiky a mezer, použije se v URL a hlasování
    "name": "Zobrazovaný název",
    "menu_url": "https://...",          # stránka, kde restaurace zveřejňuje denní menu
    "address": "Ulice 123, Praha",      # volitelné
    "parser": "generic",                # "generic" = heuristika níže, nebo jméno vlastního parseru
}

Pokud pro restauraci není zaregistrovaný vlastní parser (viz parsers/registry.py),
použije se obecná heuristika (parsers/generic.py), která z textu stránky hledá
řádky s cenou (např. "Svíčková na smetaně ... 159 Kč"). Funguje překvapivě
dobře na jednoduché weby, ale u složitějších (např. menu jako obrázek, PDF,
nebo JS aplikace) bude potřeba napsat parser na míru, nebo je to nedostupné
úplně (viz poznámky níže u vynechaných restaurací).
"""

RESTAURANTS = [
    # Smíchovská krčma vynechána - jejich "Polední menu" tab se dotahuje
    # až přes JavaScript (a mimo dobu výdeje ukazuje jen informační
    # hlášku), takže obyčejné stažení HTML na to nestačí. Zkoušeli jsme
    # headless prohlížeč (Playwright), ale na free tieru Renderu s tím
    # byly komplikace (chybějící binárka prohlížeče po instalaci) - zatím
    # odloženo, můžeme se k tomu vrátit později.
    #
    # Zlatý klas vynechán ze stejného důvodu - "Denní menu" sekce se plní
    # přes JavaScript.
    {
        "id": "corleone-andel",
        "name": "Corleone Anděl",
        "menu_url": "https://www.corleone.cz/poledni-menu-andel",
        "address": "Na Bělidle 42, Praha 5 Smíchov",
        "parser": "corleone-andel",
        # Polední menu jen ve všední dny 11-15h - o víkendu appka pro
        # tuhle restauraci ukáže, že se menu nenašlo (a je to správně).
    },
    {
        "id": "le-camille",
        "name": "Le Camille",
        "menu_url": "https://www.lecamille.cz/menu-tydenni",
        "address": "Štefánikova 316/8, Praha 5",
        "parser": "le-camille",
    },
]
