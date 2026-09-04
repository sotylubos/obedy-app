"""
Hlasování kolegů, kam se dnes půjde na oběd.

Jednoduché schéma: jeden hlas na osobu a den. `voter_id` je anonymní ID,
které si frontend vygeneruje a uloží do localStorage prohlížeče (žádné
přihlašování). Kliknutí na restauraci, pro kterou už člověk hlasoval,
hlas zase odebere (toggle).

Den se počítá podle času v Praze, aby appka fungovala správně, i kdyby
server běžel v jiném časovém pásmu.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from zoneinfo import ZoneInfo

DB_PATH = Path(__file__).resolve().parent / "votes.db"
PRAGUE_TZ = ZoneInfo("Europe/Prague")


def today_str() -> str:
    return datetime.now(PRAGUE_TZ).date().isoformat()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            voter_id TEXT NOT NULL,
            day TEXT NOT NULL,
            restaurant_id TEXT NOT NULL,
            PRIMARY KEY (voter_id, day)
        )
        """
    )
    return conn


def get_counts(day: Optional[str] = None) -> Dict[str, int]:
    day = day or today_str()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT restaurant_id, COUNT(*) FROM votes WHERE day = ? GROUP BY restaurant_id",
            (day,),
        ).fetchall()
    return {restaurant_id: count for restaurant_id, count in rows}


def get_voter_choice(voter_id: str, day: Optional[str] = None) -> Optional[str]:
    day = day or today_str()
    with _connect() as conn:
        row = conn.execute(
            "SELECT restaurant_id FROM votes WHERE voter_id = ? AND day = ?",
            (voter_id, day),
        ).fetchone()
    return row[0] if row else None


def toggle_vote(voter_id: str, restaurant_id: str, day: Optional[str] = None) -> Optional[str]:
    """Přepne hlas dané osoby. Vrací restaurant_id, pro kterou má osoba
    po provedení akce hlas nastavený (nebo None, pokud hlas zrušila)."""
    day = day or today_str()
    with _connect() as conn:
        current = conn.execute(
            "SELECT restaurant_id FROM votes WHERE voter_id = ? AND day = ?",
            (voter_id, day),
        ).fetchone()

        if current and current[0] == restaurant_id:
            conn.execute(
                "DELETE FROM votes WHERE voter_id = ? AND day = ?", (voter_id, day)
            )
            conn.commit()
            return None

        conn.execute(
            """
            INSERT INTO votes (voter_id, day, restaurant_id) VALUES (?, ?, ?)
            ON CONFLICT (voter_id, day) DO UPDATE SET restaurant_id = excluded.restaurant_id
            """,
            (voter_id, day, restaurant_id),
        )
        conn.commit()
        return restaurant_id
