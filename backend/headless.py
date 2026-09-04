"""
Pomocná vrstva pro restaurace, jejichž denní menu se dotahuje / vykresluje
až přes JavaScript v prohlížeči (Zlatý klas, Smíchovská krčma). Pro tyhle
weby prosté HTTP stažení (requests) nestačí - potřebujeme skutečný, byť
neviditelný prohlížeč, který stránku vykreslí stejně jako člověk.

Používá Playwright (https://playwright.dev/python/). Prohlížeč se spouští
jen když vyprší cache pro danou restauraci (viz main.py, CACHE_TTL_SECONDS),
ne při každém požadavku uživatele - na hostingu s omezenou pamětí (free
tier) je tohle důležité, ať appka zbytečně neplýtvá zdroji.

DŮLEŽITÉ: aby tohle na Renderu fungovalo, musí se při buildu appky navíc
stáhnout samotný prohlížeč Chromium. To znamená upravit "Build Command"
ve Settings appky na Renderu na:

    pip install -r requirements.txt && playwright install --with-deps chromium

Bez téhle úpravy poběží appka dál (statické restaurace budou fungovat),
ale u restaurací s "fetch": "headless" v restaurants.py appka nahlásí
chybu, že Chromium není nainstalované.
"""

import logging
from typing import Optional

from playwright.sync_api import sync_playwright

log = logging.getLogger("headless")


def fetch_rendered_html(
    url: str,
    click_text: Optional[str] = None,
    wait_ms: int = 2500,
    timeout_ms: int = 25000,
) -> str:
    """Otevře stránku v headless Chromiu, počká na dokreslení JS obsahu,
    volitelně klikne na element s daným textem (např. na tab "Polední
    menu") a vrátí finální vykreslené HTML."""

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        try:
            page = browser.new_page()
            page.set_default_timeout(timeout_ms)
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(wait_ms)

            if click_text:
                try:
                    page.get_by_text(click_text, exact=False).first.click(timeout=5000)
                    page.wait_for_timeout(wait_ms)
                except Exception:
                    log.warning("Nepodařilo se kliknout na '%s' na %s", click_text, url)

            return page.content()
        finally:
            browser.close()
