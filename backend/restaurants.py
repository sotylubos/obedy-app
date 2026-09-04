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
Volitelné klíče:
{
    "fetch": "headless",    # jinak výchozí "static" (obyčejný requests.get)
    "click_text": "...",    # text tlačítka/tabu, na který má headless prohlížeč před čtením kliknout
}

Restaurace s "fetch": "headless" se otevírají přes neviditelný prohlížeč
(Playwright) - používá se u webů, které svůj obsah dotahují/vykreslují až
přes JavaScript, takže obyčejné stažení HTML na nich nic nenajde. Je to
pomalejší a náročnější na zdroje, proto se používá jen tam, kde to jinak
nejde - viz poznámky u Zlatého klasu a Smíchovské krčmy níže.
"""

RESTAURANTS = [
    {
        "id": "zlaty-klas",
        "name": "Zlatý klas",
        "menu_url": "https://zlatyklas.cz/#denni-menu",
        "address": "Plzeňská 9, Praha 5 (Palác Křižík - Anděl)",
        "parser": "generic",
        "fetch": "headless",
        # EXPERIMENTÁLNÍ: sekce "Denní menu" se plní až přes JavaScript,
        # takže to zkoušíme přes headless prohlížeč. Nemáme jak si ověřit
        # přesnou strukturu předem - uvidíme podle výsledku na Renderu,
        # jestli obecná heuristika (hledání řádků s cenou) stačí, nebo
        # bude potřeba parser na míru.
    },
    {
        "id": "smichovska-krcma",
        "name": "Smíchovská krčma",
        "menu_url": "https://smichovska-krcma.cz/jidelni-listek",
        "address": "Na Čečeličce 402/12, Praha 5",
        "parser": "generic",
        "fetch": "headless",
        "click_text": "Polední menu",
        # EXPERIMENTÁLNÍ: appka otevře stránku, počká, klikne na tab
        # "Polední menu" a teprve pak čte obsah. Mimo dobu výdeje menu
        # web sám hlásí, že menu teď není k dispozici - v tom případě
        # appka správně ukáže "menu se nenašlo", není to chyba.
    },
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
