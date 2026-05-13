"""
Fin-VQA Analysis History Manager Module.
Handles persistent storage of AI analysis results using SQLite for backtesting.
"""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from src.config import LOG_DATE_FORMAT

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "analysis_history.db"


class AnalysisHistory:
    """Manages persistent analysis history storage via SQLite."""

    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialized the database schema."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticker TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        sentiment TEXT,
                        confidence INTEGER,
                        price_at_analysis REAL,
                        model_used TEXT,
                        summary TEXT,
                        full_analysis TEXT
                    )
                """)
                conn.commit()
            logger.info("Analysis history database was initialized.")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def save_analysis(
        self, ticker: str, sentiment: str, confidence: int,
        price: float, model_used: str, summary: str, full_analysis: str,
    ) -> bool:
        """Saved an analysis record to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO analysis_history
                       (ticker, timestamp, sentiment, confidence, price_at_analysis,
                        model_used, summary, full_analysis)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ticker,
                        datetime.now().strftime(LOG_DATE_FORMAT),
                        sentiment,
                        confidence,
                        price,
                        model_used,
                        summary,
                        full_analysis,
                    ),
                )
                conn.commit()
            logger.info(f"Analysis for {ticker} was saved to history.")
            return True
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}")
            return False

    def get_history(self, ticker: Optional[str] = None, limit: int = 50) -> pd.DataFrame:
        """Retrieved analysis history, optionally filtered by ticker."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if ticker:
                    query = (
                        "SELECT id, ticker, timestamp, sentiment, confidence, "
                        "price_at_analysis, model_used, summary "
                        "FROM analysis_history WHERE ticker = ? "
                        "ORDER BY timestamp DESC LIMIT ?"
                    )
                    df = pd.read_sql_query(query, conn, params=(ticker, limit))
                else:
                    query = (
                        "SELECT id, ticker, timestamp, sentiment, confidence, "
                        "price_at_analysis, model_used, summary "
                        "FROM analysis_history ORDER BY timestamp DESC LIMIT ?"
                    )
                    df = pd.read_sql_query(query, conn, params=(limit,))
            return df
        except Exception as e:
            logger.error(f"Failed to retrieve history: {e}")
            return pd.DataFrame()

    def get_record_count(self) -> int:
        """Returned total number of analysis records."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM analysis_history")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def delete_record(self, record_id: int) -> bool:
        """Deleted a specific analysis record by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM analysis_history WHERE id = ?", (record_id,))
                conn.commit()
            logger.info(f"Record {record_id} was deleted from history.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete record {record_id}: {e}")
            return False

    def clear_history(self) -> bool:
        """Cleared all analysis history records."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM analysis_history")
                conn.commit()
            logger.info("All analysis history was cleared.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear history: {e}")
            return False
