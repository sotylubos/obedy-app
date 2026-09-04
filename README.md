# Obědová appka

Webová appka pro kurátorovaný seznam restaurací: stahuje jejich denní menu
přímo z jejich vlastních webů a kolegové mohou hlasovat, kam se dnes půjde
na oběd. Backend je Python/FastAPI, frontend obyčejné HTML/CSS/JS.

## Jak to spustit

Potřebuješ Python 3.10+.

```bash
cd backend
python -m venv venv
source venv/bin/activate      # na Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn main:app --reload --port 8000
```

Pak otevři **http://localhost:8000** v prohlížeči (klidně i z více zařízení
ve stejné síti, ať můžou kolegové hlasovat).

## Jak přidat restauraci

1. Otevři `backend/restaurants.py` a přidej položku se `id`, `name`,
   `menu_url` a volitelně `address` — viz šablona přímo v souboru.
2. Necháš `"parser": "generic"` — obecná heuristika (`backend/parsers/generic.py`)
   zkusí z textu stránky vytáhnout řádky s cenou. Funguje na jednoduché weby,
   ale ne vždy spolehlivě.
3. Pokud obecný parser menu nerozezná (appka u restaurace ukáže chybovou
   hlášku), pošli mi odkaz na její web a napíšu pro ni parser na míru podle
   skutečné HTML struktury — přidá se jako nový soubor do `backend/parsers/`
   a zaregistruje v `backend/parsers/registry.py`.

Data se cachují na 3 hodiny na restauraci, tlačítko "Stáhnout znovu" cache
smaže a vynutí čerstvé stažení.

## Hlasování kolegů

Každý prohlížeč si při první návštěvě vygeneruje anonymní ID (uložené
v `localStorage`, žádné přihlašování). Kliknutím na "Hlasovat" se hlas
uloží do `backend/votes.db` (SQLite) pro aktuální den (počítáno podle
pražského času). Opětovné kliknutí na stejnou restauraci hlas zruší.
Restaurace s nejvíce hlasy dostane na kartě rámeček a štítek "VEDE".
Stránka si počty hlasů sama obnovuje každých 20 sekund, ať to kolegové
vidí bez ručního refreshe.

Hlasy se nikde ručně nemažou — pro nový den se automaticky počítají znovu,
protože se filtrují podle dnešního data.

## Restaurace s JavaScriptem (Zlatý klas, Smíchovská krčma)

Tyhle dvě restaurace mají denní menu, které se dotahuje/vykresluje až přes
JavaScript v prohlížeči - obyčejné stažení HTML na nich nic nenajde. Appka
proto pro ně používá neviditelný prohlížeč (Playwright/Chromium), který
stránku skutečně otevře, počká na JS a teprve pak čte výsledek. Je to
experimentální řešení - nemáme jak si dopředu ověřit přesnou strukturu
těch stránek, takže první ostrá zkouška proběhne až po nasazení. Pokud
appka u nich hlásí "menu se nenašlo" i v době, kdy menu podávají, pošli mi
vědět a parser pro danou restauraci doladíme.

**Důležité: aby tohle na Renderu fungovalo, je potřeba upravit Build
Command appky** (nejen `pip install -r requirements.txt`), protože se
musí navíc stáhnout samotný prohlížeč Chromium:

1. Na Renderu otevři appku `obedy-app` → **Settings**.
2. Najdi pole **Build Command** a nastav ho na:
   ```
   pip install -r requirements.txt && playwright install --with-deps chromium
   ```
3. Ulož změny (**Save Changes**) - Render appku znovu nasadí s novým
   nastavením. Build bude tentokrát o dost pomalejší (stahuje se prohlížeč),
   klidně pár minut.

Tohle je zátěžnější na paměť i čas buildu než zbytek appky, takže pokud by
to na free tieru dělalo problémy (build selže, appka spadne na nedostatek
paměti), dáme vědět a buď to doladíme, nebo tyhle dvě restaurace zase
dočasně vypneme.

## Nasazení mimo localhost

Pro trvalý provoz (např. na malém serveru nebo Raspberry Pi):

- Spusť `uvicorn main:app --host 0.0.0.0 --port 8000` a appku zpřístupni ve
  své síti / přes reverzní proxy (nginx, Caddy).
- Zvaž periodické spouštění scraperu přes cron místo spoléhání na cache
  s TTL (např. `python scraper.py praha-1` každé ráno v 8:00), pokud chceš
  mít jistotu čerstvých dat bez čekání na první request.

## Poznámka k etice scrapingu

Appka stahuje jen veřejně dostupné stránky restaurací, které si sám/sama
vybereš, s rozumnou frekvencí (cache na 3 hodiny). U každé restaurace je
dobré mrknout na její `robots.txt` a podmínky užití, pokud appku budeš
provozovat déle nebo pro víc lidí.
