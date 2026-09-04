import logging
from typing import Dict

import requests

from models import RestaurantMenu
from parsers.registry import get_parser

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("scraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ObedyApp/1.0; osobni pouziti)"
}
REQUEST_TIMEOUT = 15


def fetch_menu(restaurant: Dict) -> RestaurantMenu:
    """Stáhne a naparsuje menu jedné restaurace podle její konfigurace
    v restaurants.py. Chyby nepropaguje výš, ale uloží je do pole `error`,
    aby výpadek jedné restaurace nesrazil zbytek appky."""

    result = RestaurantMenu(
        id=restaurant["id"],
        name=restaurant["name"],
        url=restaurant.get("menu_url"),
        address=restaurant.get("address"),
    )

    try:
        resp = requests.get(restaurant["menu_url"], headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
    except requests.RequestException as e:
        log.warning("Stažení menu pro %s selhalo: %s", restaurant["id"], e)
        result.error = f"Nepodařilo se stáhnout stránku ({e})"
        return result

    parser_name = restaurant.get("parser", "generic")
    parse_fn = get_parser(parser_name)

    try:
        result.items = parse_fn(resp.text)
    except Exception as e:  # parser je "cizí" kód na míru webu, buďme opatrní
        log.exception("Parsování menu pro %s selhalo", restaurant["id"])
        result.error = f"Nepodařilo se rozpoznat menu ({e})"
        return result

    if not result.items:
        result.error = "Na stránce se nenašly žádné položky menu (možná se změnila struktura webu)"

    return result
