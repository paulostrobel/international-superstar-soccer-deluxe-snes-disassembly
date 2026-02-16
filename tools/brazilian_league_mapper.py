#!/usr/bin/env python3
"""
Brazilian Serie A Stats Mapper for International Superstar Soccer Deluxe (SNES)

Scrapes player stats from fbref.com for the Brazilian Serie A and generates
assembly data files compatible with the ISSD SNES disassembly project.

Output format matches the data structures in Routine_Macros_ISSD.asm:
  - Player names: 20 players x 8 characters each (TallMenuText encoding)
  - Player stats: 20 players x 8 bytes each (packed nibble format)

Usage:
    python3 brazilian_league_mapper.py [--season YEAR] [--output DIR]
    python3 brazilian_league_mapper.py --season 2024 --output ./output
    python3 brazilian_league_mapper.py --skip-extra-stats   # faster, less accurate
    python3 brazilian_league_mapper.py --fetcher selenium    # force Selenium backend
    python3 brazilian_league_mapper.py --html-dir ./pages    # use saved HTML files

Data source: https://fbref.com/en/comps/24/Serie-A-Stats
Rate limit: 1 request per 6 seconds (fbref.com policy)

Requirements:
    pip install beautifulsoup4 lxml cloudscraper

    Optional (if cloudscraper is blocked by Cloudflare v3):
        pip install undetected-chromedriver selenium
        (also requires Chrome/Chromium browser installed)

    Offline fallback:
        Save fbref pages from your browser into a directory and use --html-dir
"""

import requests
import time
import os
import sys
import argparse
import json
import re
import atexit
import hashlib
import logging
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 is required. Install with:")
    print("  pip install beautifulsoup4 lxml cloudscraper")
    sys.exit(1)

# Optional: cloudscraper (handles Cloudflare JS challenges)
HAS_CLOUDSCRAPER = False
try:
    import cloudscraper
    HAS_CLOUDSCRAPER = True
except ImportError:
    pass

# Optional: Selenium + undetected-chromedriver (full browser fallback)
HAS_SELENIUM = False
try:
    import undetected_chromedriver as uc
    from selenium.webdriver.support.ui import WebDriverWait
    HAS_SELENIUM = True
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================================
# ISSD Game Constants & Encoding
# ============================================================================

# Character encoding table matching tables/fonts/TallMenuText.txt
# Maps ASCII characters to SNES tile indices used by the game's text engine.
TALL_MENU_TEXT_ENCODING = {
    " ": 0x00,
    "!": 0x52, ".": 0x54, "+": 0x56, "-": 0x57,
    "%": 0x58, "/": 0x59, "'": 0x5A, "~": 0x5B,
    ":": 0x5C, "?": 0x5D,
    "0": 0x5E, "1": 0x5F, "2": 0x60, "3": 0x61,
    "4": 0x62, "5": 0x63, "6": 0x64, "7": 0x65,
    "8": 0x66, "9": 0x67,
    "A": 0x68, "B": 0x69, "C": 0x6A, "D": 0x6B,
    "E": 0x6C, "F": 0x6D, "G": 0x6E, "H": 0x6F,
    "I": 0x70, "J": 0x71, "K": 0x72, "L": 0x73,
    "M": 0x74, "N": 0x75, "O": 0x76, "P": 0x77,
    "Q": 0x78, "R": 0x79, "S": 0x7A, "T": 0x7B,
    "U": 0x7C, "V": 0x7D, "W": 0x7E, "X": 0x7F,
    "Y": 0x80, "Z": 0x81,
    "a": 0x82, "b": 0x83, "c": 0x84, "d": 0x85,
    "e": 0x86, "f": 0x87, "g": 0x88, "h": 0x89,
    "i": 0x8A, "j": 0x8B, "k": 0x8C, "l": 0x8D,
    "m": 0x8E, "n": 0x8F, "o": 0x90, "p": 0x91,
    "q": 0x92, "r": 0x93, "s": 0x94, "t": 0x95,
    "u": 0x96, "v": 0x97, "w": 0x98, "x": 0x99,
    "y": 0x9A, "z": 0x9B,
}

PLAYERS_PER_TEAM = 20  # Fixed roster size in ISSD
NAME_WIDTH = 8         # Fixed name width in bytes

# Position byte values used in the 8-byte stat format (DATA_87980E)
POS_GK = 0x00
POS_DF = 0x04
POS_MF = 0x08
POS_FW = 0x0D

# Known ISSD stat names mapped to their byte/nibble positions
STAT_LAYOUT = """
Player stat format (8 bytes, DATA_87980E style):
  Byte 0: Position type  ($00=GK, $04=DF, $08=MF, $0D=FW)
  Byte 1: Speed[7:4]     | KickPower[3:0]
  Byte 2: Dribbling[7:4] | Heading[3:0]
  Byte 3: Stamina[7:4]   | Defense[3:0]
  Byte 4: Passing[7:4]   | Aggression[3:0]
  Byte 5: $00 (reserved)
  Byte 6: $00 (reserved)
  Byte 7: $00 (reserved)

Each stat is a 4-bit nibble in range 0-9.
"""


# ============================================================================
# Accent / Unicode Normalization
# ============================================================================

ACCENT_MAP = {
    "á": "a", "à": "a", "ã": "a", "â": "a", "ä": "a", "å": "a",
    "é": "e", "è": "e", "ê": "e", "ë": "e",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "õ": "o", "ô": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ý": "y", "ÿ": "y",
    "ñ": "n", "ç": "c",
    "Á": "A", "À": "A", "Ã": "A", "Â": "A", "Ä": "A", "Å": "A",
    "É": "E", "È": "E", "Ê": "E", "Ë": "E",
    "Í": "I", "Ì": "I", "Î": "I", "Ï": "I",
    "Ó": "O", "Ò": "O", "Õ": "O", "Ô": "O", "Ö": "O",
    "Ú": "U", "Ù": "U", "Û": "U", "Ü": "U",
    "Ý": "Y", "Ñ": "N", "Ç": "C",
    "ø": "o", "Ø": "O", "ß": "ss",
    "ğ": "g", "Ğ": "G", "ş": "s", "Ş": "S",
    "ı": "i", "İ": "I",
}


# ============================================================================
# Web Scraping
# ============================================================================

FBREF_BASE_URL = "https://fbref.com"
FBREF_SERIE_A_COMP_ID = 24

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Connection": "keep-alive",
}

REQUEST_DELAY = 6  # fbref rate limit: 1 req / 6 seconds


# ============================================================================
# Multi-Backend Fetcher (cloudscraper → Selenium → requests)
# ============================================================================

# Active fetcher state (set by init_fetcher)
_fetcher_type = None   # "cloudscraper" | "selenium" | "requests" | "offline"
_fetcher_session = None  # the session/driver object
_html_dir = None         # path for offline mode


def init_fetcher(backend="auto", html_dir=None):
    """
    Initialize the HTTP fetcher backend.

    Priority for "auto":  cloudscraper → selenium → requests
    """
    global _fetcher_type, _fetcher_session, _html_dir

    # Offline mode overrides everything
    if html_dir:
        _html_dir = html_dir
        _fetcher_type = "offline"
        logger.info(f"Fetcher: OFFLINE mode (reading from {html_dir})")
        return "offline"

    if backend == "auto":
        if HAS_CLOUDSCRAPER:
            backend = "cloudscraper"
        elif HAS_SELENIUM:
            backend = "selenium"
        else:
            backend = "requests"

    if backend == "cloudscraper":
        if not HAS_CLOUDSCRAPER:
            logger.error("cloudscraper not installed: pip install cloudscraper")
            sys.exit(1)
        _fetcher_session = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "desktop": True},
        )
        _fetcher_session.headers.update(HEADERS)
        _fetcher_type = "cloudscraper"
        logger.info("Fetcher: cloudscraper (Cloudflare JS bypass)")

    elif backend == "selenium":
        if not HAS_SELENIUM:
            logger.error(
                "Selenium not installed: pip install undetected-chromedriver selenium"
            )
            sys.exit(1)
        options = uc.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        _fetcher_session = uc.Chrome(options=options)
        _fetcher_type = "selenium"
        atexit.register(_cleanup_selenium)
        logger.info("Fetcher: Selenium + undetected-chromedriver (full browser)")

    elif backend == "requests":
        _fetcher_session = requests.Session()
        _fetcher_session.headers.update(HEADERS)
        _fetcher_type = "requests"
        logger.info("Fetcher: plain requests (may get 403 from Cloudflare)")

    else:
        logger.error(f"Unknown fetcher backend: {backend}")
        sys.exit(1)

    return _fetcher_type


def _cleanup_selenium():
    """Shut down the Selenium browser on exit."""
    global _fetcher_session
    if _fetcher_type == "selenium" and _fetcher_session:
        try:
            _fetcher_session.quit()
        except Exception:
            pass
        _fetcher_session = None


def _url_to_filename(url):
    """Convert a URL to a safe filename for offline mode."""
    # Extract meaningful path parts
    path = url.replace(FBREF_BASE_URL, "").strip("/")
    # Sanitize for filesystem
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", path)
    # Add a short hash to avoid collisions
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    return f"{safe[:80]}_{url_hash}.html"


def _load_offline(url):
    """Load a page from the offline HTML directory."""
    target = _url_to_filename(url)
    target_path = os.path.join(_html_dir, target)

    # Also try a simpler name match (user may have saved as "flamengo.html")
    candidates = [target_path]
    # Try matching any file that contains relevant URL fragments
    if os.path.isdir(_html_dir):
        url_parts = url.replace(FBREF_BASE_URL, "").strip("/").split("/")
        for f in os.listdir(_html_dir):
            if f.endswith(".html") or f.endswith(".htm"):
                flow = f.lower()
                for part in url_parts:
                    if len(part) > 3 and part.lower() in flow:
                        candidates.append(os.path.join(_html_dir, f))
                        break

    for path in candidates:
        if os.path.isfile(path):
            logger.info(f"OFFLINE: loading {path}")
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                return fh.read()

    logger.warning(f"OFFLINE: no file found for {url}")
    logger.warning(f"  Expected: {target_path}")
    logger.warning(f"  Tip: open the URL in your browser, Ctrl+S to save as HTML,")
    logger.warning(f"       then place it in {_html_dir}/")
    return None


def _fetch_with_cloudscraper(url, retries=3):
    """Fetch using cloudscraper (handles Cloudflare JS challenges)."""
    for attempt in range(retries):
        try:
            logger.info(f"GET [cloudscraper] {url}")
            resp = _fetcher_session.get(url, timeout=30)
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return resp.text
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                logger.warning(f"Rate limited (429). Waiting {wait}s...")
                time.sleep(wait)
            elif resp.status_code == 403:
                logger.warning(
                    f"HTTP 403 from cloudscraper (attempt {attempt + 1}/{retries})"
                )
                # Cloudflare may need a longer delay before retry
                time.sleep(REQUEST_DELAY * 3)
            else:
                logger.warning(f"HTTP {resp.status_code} — retrying...")
                time.sleep(REQUEST_DELAY * 2)
        except Exception as exc:
            logger.error(f"cloudscraper error: {exc}")
            time.sleep(REQUEST_DELAY * 2)
    return None


def _fetch_with_selenium(url, retries=3):
    """Fetch using Selenium headless browser."""
    for attempt in range(retries):
        try:
            logger.info(f"GET [selenium] {url}")
            _fetcher_session.get(url)
            # Wait for page to fully load
            time.sleep(3)
            # Check for Cloudflare challenge page and wait extra if needed
            page = _fetcher_session.page_source
            if "Just a moment" in page or "Checking your browser" in page:
                logger.info("  Cloudflare challenge detected, waiting...")
                time.sleep(8)
                page = _fetcher_session.page_source
            if len(page) > 1000:  # sanity check
                time.sleep(REQUEST_DELAY)
                return page
            logger.warning(f"  Page too small ({len(page)} bytes), retrying...")
            time.sleep(REQUEST_DELAY * 2)
        except Exception as exc:
            logger.error(f"Selenium error: {exc}")
            time.sleep(REQUEST_DELAY * 2)
    return None


def _fetch_with_requests(url, retries=3):
    """Fetch using plain requests (likely to get 403 from Cloudflare)."""
    for attempt in range(retries):
        try:
            logger.info(f"GET [requests] {url}")
            resp = _fetcher_session.get(url, timeout=30)
            if resp.status_code == 200:
                time.sleep(REQUEST_DELAY)
                return resp.text
            if resp.status_code == 429:
                wait = 60 * (attempt + 1)
                logger.warning(f"Rate limited (429). Waiting {wait}s...")
                time.sleep(wait)
            else:
                logger.warning(f"HTTP {resp.status_code} — retrying...")
                time.sleep(REQUEST_DELAY * 2)
        except requests.RequestException as exc:
            logger.error(f"Request error: {exc}")
            time.sleep(REQUEST_DELAY * 2)
    return None


def fetch_page(url, retries=3):
    """
    Fetch a page using the active backend, respecting fbref.com rate limits.

    If the primary backend returns 403/None and a fallback is available,
    automatically escalates to the next backend.
    """
    global _fetcher_type, _fetcher_session

    if _fetcher_type == "offline":
        return _load_offline(url)

    # Try the configured backend first
    if _fetcher_type == "cloudscraper":
        result = _fetch_with_cloudscraper(url, retries)
        if result:
            return result
        # Auto-fallback to Selenium if available
        if HAS_SELENIUM:
            logger.warning("cloudscraper failed — falling back to Selenium...")
            init_fetcher("selenium")
            result = _fetch_with_selenium(url, retries)
            if result:
                return result

    elif _fetcher_type == "selenium":
        result = _fetch_with_selenium(url, retries)
        if result:
            return result

    elif _fetcher_type == "requests":
        result = _fetch_with_requests(url, retries)
        if result:
            return result
        # Auto-fallback: try cloudscraper if available
        if HAS_CLOUDSCRAPER:
            logger.warning("requests failed — falling back to cloudscraper...")
            init_fetcher("cloudscraper")
            result = _fetch_with_cloudscraper(url, retries)
            if result:
                return result

    logger.error(f"FAILED all backends for: {url}")
    return None


def uncomment_html(html):
    """Remove HTML comments wrapping hidden fbref tables."""
    return html.replace("<!--", "").replace("-->", "")


def _find_table(soup, id_pattern):
    """Find a <table> whose id matches a regex pattern."""
    tbl = soup.find("table", {"id": re.compile(id_pattern)})
    if tbl:
        return tbl
    # Fallback: first stats_table
    tables = soup.find_all("table", {"class": "stats_table"})
    return tables[0] if tables else None


def _parse_cell(row, data_stat, as_type="str"):
    """Extract text from a <td>/<th> by its data-stat attribute."""
    cell = row.find(["td", "th"], {"data-stat": data_stat})
    if cell is None:
        return "" if as_type == "str" else 0
    txt = cell.get_text(strip=True).replace(",", "")
    if as_type == "int":
        return _safe_int(txt)
    if as_type == "float":
        return _safe_float(txt)
    return txt


def _safe_int(s):
    try:
        return int(s)
    except (ValueError, TypeError):
        return 0


def _safe_float(s):
    try:
        return float(s)
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# Scraping individual pages
# ---------------------------------------------------------------------------

def scrape_team_list(season=None):
    """Return list of {name, url} for all Serie A teams."""
    if season:
        url = (f"{FBREF_BASE_URL}/en/comps/{FBREF_SERIE_A_COMP_ID}"
               f"/{season}/{season}-Serie-A-Stats")
    else:
        url = f"{FBREF_BASE_URL}/en/comps/{FBREF_SERIE_A_COMP_ID}/Serie-A-Stats"

    html = fetch_page(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    teams = []
    seen = set()

    # Look for the overall standings table
    table = soup.find("table", {"id": re.compile(r"results.*overall")})
    if not table:
        # Fallback: first stats_table on the page
        for t in soup.find_all("table", {"class": "stats_table"}):
            if t.find("td", {"data-stat": "team"}):
                table = t
                break

    if not table:
        logger.error("Could not find team table on the page")
        return []

    for row in table.find_all("tr"):
        cell = row.find(["td", "th"], {"data-stat": "team"})
        if not cell:
            continue
        link = cell.find("a", href=True)
        if not link:
            continue
        name = link.get_text(strip=True)
        if name and name not in seen:
            seen.add(name)
            teams.append({"name": name, "url": FBREF_BASE_URL + link["href"]})

    logger.info(f"Found {len(teams)} teams")
    return teams


def scrape_standard_stats(team_url):
    """Scrape standard player stats from a team page. Returns list of dicts."""
    html = fetch_page(team_url)
    if not html:
        return []

    soup = BeautifulSoup(uncomment_html(html), "lxml")
    table = _find_table(soup, r"stats_standard")
    if not table:
        logger.warning("No standard stats table found")
        return []

    tbody = table.find("tbody")
    if not tbody:
        return []

    players = []
    for row in tbody.find_all("tr"):
        if row.find("th", {"scope": "row"}) is None:
            continue
        p = {
            "name":               _parse_cell(row, "player"),
            "position":           _parse_cell(row, "position"),
            "age":                _parse_cell(row, "age"),
            "games":              _parse_cell(row, "games", "int"),
            "games_starts":       _parse_cell(row, "games_starts", "int"),
            "minutes":            _parse_cell(row, "minutes", "int"),
            "goals":              _parse_cell(row, "goals", "int"),
            "assists":            _parse_cell(row, "assists", "int"),
            "xg":                 _parse_cell(row, "xg", "float"),
            "xg_assist":          _parse_cell(row, "xg_assist", "float"),
            "progressive_carries": _parse_cell(row, "progressive_carries", "int"),
            "progressive_passes": _parse_cell(row, "progressive_passes", "int"),
            "yellow_cards":       _parse_cell(row, "cards_yellow", "int"),
            "red_cards":          _parse_cell(row, "cards_red", "int"),
        }
        if p["name"]:
            players.append(p)

    logger.info(f"  Standard stats: {len(players)} players")
    return players


def _scrape_stat_table(team_url, table_id_re, fields):
    """Generic helper: scrape a named table and return {player_name: {fields}}."""
    html = fetch_page(team_url)
    if not html:
        return {}
    soup = BeautifulSoup(uncomment_html(html), "lxml")
    table = _find_table(soup, table_id_re)
    if not table:
        return {}
    tbody = table.find("tbody")
    if not tbody:
        return {}

    data = {}
    for row in tbody.find_all("tr"):
        if row.find("th", {"scope": "row"}) is None:
            continue
        name = _parse_cell(row, "player")
        if not name:
            continue
        entry = {}
        for field_name, data_stat, as_type in fields:
            entry[field_name] = _parse_cell(row, data_stat, as_type)
        data[name] = entry
    return data


def scrape_shooting(team_url):
    return _scrape_stat_table(team_url, r"stats_shooting", [
        ("shots_on_target",    "shots_on_target",       "int"),
        ("shots_total",        "shots",                 "int"),
        ("avg_shot_distance",  "average_shot_distance", "float"),
    ])


def scrape_passing(team_url):
    return _scrape_stat_table(team_url, r"stats_passing", [
        ("pass_completion_pct", "passes_pct",          "float"),
        ("progressive_passes",  "progressive_passes",  "int"),
        ("passes_completed",    "passes_completed",    "int"),
    ])


def scrape_defense(team_url):
    return _scrape_stat_table(team_url, r"stats_defense", [
        ("tackles",       "tackles",       "int"),
        ("interceptions", "interceptions", "int"),
        ("blocks",        "blocks",        "int"),
        ("tackles_won",   "tackles_won",   "int"),
    ])


def scrape_possession(team_url):
    return _scrape_stat_table(team_url, r"stats_possession", [
        ("touches",              "touches",          "int"),
        ("dribbles_completed",   "take_ons_won",     "int"),
        ("dribbles_attempted",   "take_ons",         "int"),
        ("carries",              "carries",          "int"),
        ("progressive_carries",  "progressive_carries", "int"),
    ])


def scrape_keeper(team_url):
    return _scrape_stat_table(team_url, r"stats_keeper", [
        ("saves",       "gk_saves",       "int"),
        ("save_pct",    "gk_save_pct",    "float"),
        ("clean_sheets", "gk_clean_sheets", "int"),
    ])


# ============================================================================
# Stat Mapping:  fbref data  -->  ISSD 8-byte player attributes
# ============================================================================

def clamp(val, lo=0, hi=9):
    return max(lo, min(hi, int(val)))


def scale(value, src_min, src_max):
    """Linearly scale value from [src_min, src_max] to [0.0, 1.0]."""
    if src_max <= src_min:
        return 0.5
    return max(0.0, min(1.0, (value - src_min) / (src_max - src_min)))


def compute_issd_stats(player, shoot, passing, defense, poss, keeper):
    """
    Convert scraped fbref stats into ISSD's 7 player attributes (0-9 each).

    Returns dict with: speed, kick_power, dribbling, heading,
                       stamina, defense, passing, aggression
    and list 'bytes' with the 8-byte packed representation.
    """
    pos_str = player.get("position", "").upper()
    minutes = max(player.get("minutes", 0), 1)
    games   = max(player.get("games", 0), 1)
    per90   = minutes / 90.0

    shoot_d   = shoot.get(player["name"], {})
    pass_d    = passing.get(player["name"], {})
    def_d     = defense.get(player["name"], {})
    poss_d    = poss.get(player["name"], {})
    keep_d    = keeper.get(player["name"], {})

    is_gk = "GK" in pos_str
    is_df = "DF" in pos_str
    is_mf = "MF" in pos_str
    is_fw = "FW" in pos_str

    # --- Position byte ---
    if is_gk:
        pos_byte = POS_GK
    elif is_df:
        pos_byte = POS_DF
    elif is_fw:
        pos_byte = POS_FW
    else:
        pos_byte = POS_MF

    # --- SPEED (0-9) ---
    # Based on progressive carries, dribble attempts (mobility indicators)
    prog_carries = poss_d.get("progressive_carries", 0)
    carries      = poss_d.get("carries", 0)
    carries_p90  = carries / per90 if per90 > 0 else 0
    speed_raw = scale(carries_p90, 5, 55) * 7 + 2
    if is_fw:
        speed_raw += 1
    if is_gk:
        speed_raw = max(2, speed_raw - 3)
    speed = clamp(speed_raw)

    # --- KICK POWER (0-9) ---
    # Goals, xG, shots on target
    goals    = player.get("goals", 0)
    xg       = player.get("xg", 0)
    sot      = shoot_d.get("shots_on_target", 0)
    kp_raw = (
        scale(goals, 0, 15) * 0.40
        + scale(xg, 0, 12) * 0.30
        + scale(sot, 0, 40) * 0.30
    ) * 8 + 1
    if is_gk:
        kp_raw = 3
    elif is_df:
        kp_raw = max(2, kp_raw - 1)
    kick_power = clamp(kp_raw)

    # --- DRIBBLING (0-9) ---
    drib_won = poss_d.get("dribbles_completed", 0)
    drib_att = poss_d.get("dribbles_attempted", 0)
    drib_pct = (drib_won / drib_att * 100) if drib_att > 0 else 50
    drib_raw = (
        scale(drib_won, 0, 60) * 0.6
        + scale(drib_pct, 30, 80) * 0.4
    ) * 8 + 1
    if is_gk:
        drib_raw = 2
    dribbling = clamp(drib_raw)

    # --- HEADING (0-9) ---
    # Position-biased (defenders/strikers header more)
    heading_base = 4
    if is_df:
        heading_base = 6
    elif is_fw:
        heading_base = 5
    elif is_gk:
        heading_base = 3
    heading = clamp(heading_base + goals * 0.12)

    # --- STAMINA (0-9) ---
    min_per_game = minutes / games if games > 0 else 45
    stam_raw = scale(min_per_game, 20, 90) * 7 + 2
    stamina = clamp(stam_raw)

    # --- DEFENSE (0-9) ---
    tkl  = def_d.get("tackles", 0)
    ints = def_d.get("interceptions", 0)
    blk  = def_d.get("blocks", 0)
    def_total = tkl + ints + blk
    def_raw = scale(def_total, 0, 90) * 7 + 2
    if is_gk:
        # Goalkeepers: use save percentage and clean sheets
        sv_pct = keep_d.get("save_pct", 65)
        cs     = keep_d.get("clean_sheets", 0)
        def_raw = scale(sv_pct, 55, 85) * 5 + scale(cs, 0, 15) * 3 + 2
    elif is_fw:
        def_raw = max(1, def_raw - 2)
    elif is_df:
        def_raw = min(9, def_raw + 1)
    defense_stat = clamp(def_raw)

    # --- PASSING (0-9) ---
    pass_pct  = pass_d.get("pass_completion_pct", 70)
    prog_pass = pass_d.get("progressive_passes", 0)
    assists   = player.get("assists", 0)
    pass_raw = (
        scale(pass_pct, 55, 92) * 0.4
        + scale(prog_pass, 0, 80) * 0.3
        + scale(assists, 0, 10) * 0.3
    ) * 8 + 1
    if is_gk:
        pass_raw = max(2, pass_raw - 2)
    passing_stat = clamp(pass_raw)

    # --- AGGRESSION (0-9) ---
    yc = player.get("yellow_cards", 0)
    rc = player.get("red_cards", 0)
    agg_raw = min(9, int(yc * 0.6 + rc * 2.5) + 2)
    aggression = clamp(agg_raw)

    # --- Pack into 8 bytes ---
    byte1 = ((speed & 0x0F) << 4) | (kick_power & 0x0F)
    byte2 = ((dribbling & 0x0F) << 4) | (heading & 0x0F)
    byte3 = ((stamina & 0x0F) << 4) | (defense_stat & 0x0F)
    byte4 = ((passing_stat & 0x0F) << 4) | (aggression & 0x0F)

    return {
        "pos_byte": pos_byte,
        "bytes": [pos_byte, byte1, byte2, byte3, byte4, 0x00, 0x00, 0x00],
        "speed": speed,
        "kick_power": kick_power,
        "dribbling": dribbling,
        "heading": heading,
        "stamina": stamina,
        "defense": defense_stat,
        "passing": passing_stat,
        "aggression": aggression,
    }


# ============================================================================
# Name Formatting
# ============================================================================

def strip_accents(text):
    """Replace accented/unicode characters with ASCII equivalents."""
    for src, dst in ACCENT_MAP.items():
        text = text.replace(src, dst)
    return text


def format_name_8char(full_name):
    """
    Convert a real player name into ISSD's 8-character padded format.

    Follows the naming conventions found in the original ROM data:
      - Prefer surname / known name
      - Center-pad short names with spaces
      - Truncate at 8 characters
      - Strip accented characters to ASCII

    Examples:
        "Neymar da Silva Santos Junior" -> " Neymar "
        "Gabriel Barbosa"               -> "G.Barbos"
        "Endrick Felipe Moreira"        -> "Endrick "
        "Vinicius Jose de Oliveira"     -> "Oliveira"
    """
    name = strip_accents(full_name.strip())

    # Keep only characters that exist in the encoding table
    name = "".join(c for c in name if c in TALL_MENU_TEXT_ENCODING)

    parts = name.split()
    if not parts:
        return "Unknown "

    # Skip common Brazilian name prepositions
    skip = {"da", "de", "do", "dos", "das", "e", "di"}

    significant = [p for p in parts if p.lower() not in skip]
    if not significant:
        significant = parts

    if len(significant) == 1:
        chosen = significant[0]
    elif len(significant[-1]) <= NAME_WIDTH:
        chosen = significant[-1]
    else:
        # Abbreviate: "G.Barbos" style
        chosen = significant[0][0] + "." + significant[-1][: NAME_WIDTH - 2]

    # Truncate
    chosen = chosen[:NAME_WIDTH]

    # Center-pad with spaces (matches ROM style: " Santos ", "Pardilla")
    pad_total = NAME_WIDTH - len(chosen)
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    chosen = " " * pad_left + chosen + " " * pad_right

    return chosen


# ============================================================================
# Roster Selection
# ============================================================================

def select_roster(players):
    """
    Pick the best 20 players for the ISSD roster.

    Ensures positional balance:  2 GK, 6 DF, 7 MF, 5 FW
    Ties broken by minutes played.
    """
    by_minutes = sorted(players, key=lambda p: p.get("minutes", 0), reverse=True)

    gk = [p for p in by_minutes if "GK" in p.get("position", "").upper()]
    df = [p for p in by_minutes if "DF" in p.get("position", "").upper()]
    mf = [p for p in by_minutes if "MF" in p.get("position", "").upper()]
    fw = [p for p in by_minutes if "FW" in p.get("position", "").upper()]

    roster = []
    roster.extend(gk[:2])
    roster.extend(df[:6])
    roster.extend(mf[:7])
    roster.extend(fw[:5])

    # Fill remaining slots from any position
    used = {p["name"] for p in roster}
    for p in by_minutes:
        if len(roster) >= PLAYERS_PER_TEAM:
            break
        if p["name"] not in used:
            roster.append(p)
            used.add(p["name"])

    # Sort: GK → DF → MF → FW
    order = {"GK": 0, "DF": 1, "MF": 2, "FW": 3}

    def pos_key(p):
        for tag, idx in order.items():
            if tag in p.get("position", "").upper():
                return idx
        return 2

    roster.sort(key=pos_key)
    return roster[:PLAYERS_PER_TEAM]


# ============================================================================
# Assembly Output
# ============================================================================

def sanitize_label(name):
    """Convert a team name into a valid assembly label fragment."""
    s = strip_accents(name)
    return re.sub(r"[^A-Za-z0-9]", "", s)


def generate_asm(teams_data, output_dir):
    """
    Write an assembly file with player names and stats for all teams.

    The output format directly matches Routine_Macros_ISSD.asm conventions:
      - Name data uses `table "tables/fonts/TallMenuText.txt"` + `db "..."` strings
      - Stat data uses raw `db $XX,...` hex byte entries
    """
    lines = []

    lines.append("; ======================================================================")
    lines.append("; Brazilian Serie A — Player Data for ISSD (SNES)")
    lines.append("; Auto-generated by brazilian_league_mapper.py")
    lines.append("; Source: https://fbref.com/en/comps/24/Serie-A-Stats")
    lines.append(";")
    lines.append("; Data format matches Routine_Macros_ISSD.asm (DATA_87818E / DATA_87980E)")
    lines.append(";")
    lines.append(";   Player names : 20 players x 8 chars (TallMenuText encoded)")
    lines.append(";   Player stats : 20 players x 8 bytes (packed nibble format)")
    lines.append(";     Byte 0 : Position  ($00=GK $04=DF $08=MF $0D=FW)")
    lines.append(";     Byte 1 : Speed[7:4]     | KickPower[3:0]")
    lines.append(";     Byte 2 : Dribbling[7:4]  | Heading[3:0]")
    lines.append(";     Byte 3 : Stamina[7:4]    | Defense[3:0]")
    lines.append(";     Byte 4 : Passing[7:4]    | Aggression[3:0]")
    lines.append(";     Bytes 5-7 : $00 (reserved)")
    lines.append("; ======================================================================")
    lines.append("")

    labels = [sanitize_label(t["name"]) for t in teams_data]

    # ---- Pointer tables ----
    lines.append("; Name pointer table (update DATA_878138 to reference these)")
    lines.append("BRLeague_NamePointers:")
    for i in range(0, len(labels), 4):
        chunk = labels[i : i + 4]
        ptrs = ",".join(f"BRLeague_Names_{l}" for l in chunk)
        lines.append(f"\tdw {ptrs}")
    lines.append("")

    lines.append("; Stat pointer table")
    lines.append("BRLeague_StatPointers:")
    for i in range(0, len(labels), 4):
        chunk = labels[i : i + 4]
        ptrs = ",".join(f"BRLeague_Stats_{l}" for l in chunk)
        lines.append(f"\tdw {ptrs}")
    lines.append("")

    # ---- Name data ----
    lines.append("; ------------------------------------------------------------------")
    lines.append("; Player Name Data")
    lines.append("; ------------------------------------------------------------------")
    lines.append("")
    lines.append('cleartable')
    lines.append('table "tables/fonts/TallMenuText.txt"')
    lines.append("")

    for team in teams_data:
        lbl = sanitize_label(team["name"])
        lines.append(f"; --- {team['name']} ---")
        lines.append(f"BRLeague_Names_{lbl}:")
        roster = team["roster"]
        for p in roster[:PLAYERS_PER_TEAM]:
            n8 = p["name_8char"]
            lines.append(f'\tdb "{n8}"')
        for _ in range(PLAYERS_PER_TEAM - min(len(roster), PLAYERS_PER_TEAM)):
            lines.append('\tdb "Reserve "')
        lines.append("")

    lines.append("cleartable")
    lines.append("")

    # ---- Stat data ----
    lines.append("; ------------------------------------------------------------------")
    lines.append("; Player Stat Data  (8 bytes per player)")
    lines.append("; ------------------------------------------------------------------")
    lines.append("")

    for team in teams_data:
        lbl = sanitize_label(team["name"])
        lines.append(f"; --- {team['name']} ---")
        lines.append(f"BRLeague_Stats_{lbl}:")
        roster = team["roster"]
        for p in roster[:PLAYERS_PER_TEAM]:
            sb = p["stat_bytes"]
            hexs = ",".join(f"${b:02X}" for b in sb)
            s = p["stats"]
            cmt = (
                f"  ; {p['name_8char'].strip():8s}"
                f"  Spd={s['speed']} Kck={s['kick_power']}"
                f" Drb={s['dribbling']} Hed={s['heading']}"
                f" Stm={s['stamina']} Def={s['defense']}"
                f" Pas={s['passing']} Agg={s['aggression']}"
            )
            lines.append(f"\tdb {hexs}{cmt}")
        for _ in range(PLAYERS_PER_TEAM - min(len(roster), PLAYERS_PER_TEAM)):
            lines.append("\tdb $08,$55,$44,$55,$44,$00,$00,$00  ; Reserve")
        lines.append("")

    # ---- Team ID defines ----
    lines.append("; ------------------------------------------------------------------")
    lines.append("; Team ID Defines  (add to Misc_Defines_ISSD.asm)")
    lines.append("; ------------------------------------------------------------------")
    lines.append(";")
    for i, team in enumerate(teams_data):
        lbl = sanitize_label(team["name"])
        tid = i * 2
        lines.append(f"; !Define_ISSD_TeamIDs_{lbl} = ${tid:04X}")
    lines.append("")

    outfile = os.path.join(output_dir, "BrazilianLeague_PlayerData.asm")
    with open(outfile, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info(f"ASM written: {outfile}")
    return outfile


def generate_json(teams_data, output_dir):
    """Write a JSON reference file with all scraped and mapped data."""
    out = []
    for team in teams_data:
        entry = {
            "team": team["name"],
            "label": sanitize_label(team["name"]),
            "players": [],
        }
        for p in team["roster"][:PLAYERS_PER_TEAM]:
            entry["players"].append({
                "original_name": p["original_name"],
                "game_name": p["name_8char"],
                "position": p["position"],
                "stat_bytes_hex": [f"0x{b:02X}" for b in p["stat_bytes"]],
                "stats": p["stats"],
                "source": p.get("source_stats", {}),
            })
        out.append(entry)

    outfile = os.path.join(output_dir, "BrazilianLeague_PlayerData.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    logger.info(f"JSON written: {outfile}")
    return outfile


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Brazilian Serie A → ISSD (SNES) player data mapper",
        epilog="Data source: https://fbref.com/en/comps/24/Serie-A-Stats",
    )
    parser.add_argument(
        "--season", type=str, default=None,
        help="Season year (e.g. 2024). Omit for current season.",
    )
    parser.add_argument(
        "--output", type=str, default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--cache", type=str, default="./cache",
        help="Cache directory for intermediate data",
    )
    parser.add_argument(
        "--skip-extra-stats", action="store_true",
        help="Only fetch standard stats (faster, less accurate mapping)",
    )
    parser.add_argument(
        "--fetcher", type=str, default="auto",
        choices=["auto", "cloudscraper", "selenium", "requests"],
        help=(
            "HTTP backend to use (default: auto). "
            "'auto' tries cloudscraper -> selenium -> requests."
        ),
    )
    parser.add_argument(
        "--html-dir", type=str, default=None,
        help=(
            "Path to directory with saved HTML files from fbref.com "
            "(offline mode — no network requests needed)"
        ),
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    os.makedirs(args.cache, exist_ok=True)

    # ---- Initialize fetcher ----
    active_backend = init_fetcher(args.fetcher, args.html_dir)

    backends_available = []
    if HAS_CLOUDSCRAPER:
        backends_available.append("cloudscraper")
    if HAS_SELENIUM:
        backends_available.append("selenium")
    backends_available.append("requests")

    banner = """
╔══════════════════════════════════════════════════════════════╗
║  Brazilian Serie A  -->  ISSD (SNES) Player Data Mapper     ║
║  Source: https://fbref.com/en/comps/24/Serie-A-Stats        ║
╚══════════════════════════════════════════════════════════════╝"""
    print(banner)
    print(f"  Season  : {args.season or 'current'}")
    print(f"  Output  : {args.output}")
    print(f"  Fetcher : {active_backend}  (available: {', '.join(backends_available)})")
    if args.html_dir:
        print(f"  HTML dir: {args.html_dir}")
    print()

    if active_backend == "requests" and not args.html_dir:
        print("  WARNING: Using plain 'requests' — fbref.com will likely block with 403.")
        print("           Install cloudscraper for best results:")
        print("             pip install cloudscraper")
        print("           Or use Selenium:")
        print("             pip install undetected-chromedriver selenium")
        print("           Or save pages manually and use --html-dir")
        print()

    # ---- Step 1: Team list ----
    print("[1/4] Fetching team list...")
    teams = scrape_team_list(args.season)
    if not teams:
        print("ERROR: Could not retrieve teams. fbref.com may be rate-limiting.")
        print("       Wait a few minutes and try again, or check your connection.")
        sys.exit(1)

    print(f"  Found {len(teams)} teams:")
    for t in teams:
        print(f"    - {t['name']}")
    print()

    # ---- Step 2: Per-team player stats ----
    print("[2/4] Scraping player stats per team (this may take a while)...")
    all_teams = []

    for idx, team in enumerate(teams):
        print(f"  [{idx + 1}/{len(teams)}] {team['name']}...")

        standard = scrape_standard_stats(team["url"])
        if not standard:
            logger.warning(f"  No player data for {team['name']}, skipping")
            continue

        shoot = {}
        passing = {}
        defense = {}
        poss = {}
        keeper = {}

        if not args.skip_extra_stats:
            shoot   = scrape_shooting(team["url"])
            passing = scrape_passing(team["url"])
            defense = scrape_defense(team["url"])
            poss    = scrape_possession(team["url"])
            keeper  = scrape_keeper(team["url"])

        roster = select_roster(standard)

        roster_mapped = []
        for p in roster:
            stats = compute_issd_stats(p, shoot, passing, defense, poss, keeper)
            roster_mapped.append({
                "original_name": p["name"],
                "name_8char": format_name_8char(p["name"]),
                "position": p.get("position", ""),
                "stat_bytes": stats["bytes"],
                "stats": {
                    "speed":      stats["speed"],
                    "kick_power": stats["kick_power"],
                    "dribbling":  stats["dribbling"],
                    "heading":    stats["heading"],
                    "stamina":    stats["stamina"],
                    "defense":    stats["defense"],
                    "passing":    stats["passing"],
                    "aggression": stats["aggression"],
                },
                "source_stats": {
                    "games":   p.get("games", 0),
                    "minutes": p.get("minutes", 0),
                    "goals":   p.get("goals", 0),
                    "assists": p.get("assists", 0),
                },
            })

        all_teams.append({
            "name": team["name"],
            "url": team["url"],
            "roster": roster_mapped,
        })

        # Cache per-team
        cache_path = os.path.join(
            args.cache, f"{sanitize_label(team['name'])}.json"
        )
        with open(cache_path, "w", encoding="utf-8") as cf:
            json.dump(
                {"team": team["name"],
                 "players": [{k: v for k, v in p.items() if k != "stat_bytes"}
                             for p in roster_mapped]},
                cf, indent=2, ensure_ascii=False,
            )

    if not all_teams:
        print("ERROR: No team data was scraped successfully.")
        sys.exit(1)

    print()

    # ---- Step 3: Generate ASM ----
    print("[3/4] Generating assembly output...")
    asm_file = generate_asm(all_teams, args.output)
    print(f"  -> {asm_file}")

    # ---- Step 4: Generate JSON ----
    print("[4/4] Generating JSON reference...")
    json_file = generate_json(all_teams, args.output)
    print(f"  -> {json_file}")

    # ---- Summary ----
    total_players = sum(len(t["roster"]) for t in all_teams)
    print(f"""
{'=' * 60}
  Done!  {len(all_teams)} teams, {total_players} players mapped.

  Output files:
    {asm_file}
    {json_file}

  To use in the ISSD disassembly:
    1. Copy BrazilianLeague_PlayerData.asm into the project
    2. Include it from Routine_Macros_ISSD.asm  (or replace the
       existing team data sections starting at line ~99485)
    3. Update the pointer table DATA_878138 (line 99487) to
       reference the BRLeague_Names_* labels
    4. Add the team ID defines to Misc_Defines_ISSD.asm
    5. Reassemble with Assemble_ISSD.bat
{'=' * 60}
""")


if __name__ == "__main__":
    main()
