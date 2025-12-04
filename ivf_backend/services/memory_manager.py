# ivf_backend/services/memory_manager.py
import sqlite3, json, logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from ..models.chat_models import ChatMessage, ConversationSession

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self):
        self.db_path = str(Path(__file__).parent.parent / "data" / "conversation_memory.db")
        self._init_database()

    def _init_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS conversations (session_id TEXT PRIMARY KEY, user_id TEXT, created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')), message_count INTEGER DEFAULT 0, metadata TEXT DEFAULT '{}')''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, timestamp TEXT DEFAULT (datetime('now')), FOREIGN KEY(session_id) REFERENCES conversations(session_id))''')
                cursor.execute('''CREATE INDEX IF NOT EXISTS idx_messages_session_time ON messages(session_id, timestamp)''')
            logger.info("Memory DB initialized")
        except Exception as e:
            logger.error(f"DB init error: {e}")
            raise

    def create_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT OR IGNORE INTO conversations (session_id, user_id) VALUES (?, ?)''', (session_id, user_id))
            return True
        except Exception as e:
            logger.error(f"create_session error: {e}")
            return False

    def add_message(self, session_id: str, role: str, content: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)''', (session_id, role, content))
                cursor.execute('''UPDATE conversations SET updated_at = datetime('now'), message_count = message_count + 1 WHERE session_id = ?''', (session_id,))
            return True
        except Exception as e:
            logger.error(f"add_message error: {e}")
            return False

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?''', (session_id, limit))
                rows = cursor.fetchall()
            msgs = []
            for role, content, ts in rows:
                try:
                    ts_parsed = datetime.fromisoformat(ts)
                except:
                    from datetime import datetime as dt
                    try:
                        ts_parsed = dt.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    except:
                        ts_parsed = datetime.now()
                msgs.append(ChatMessage(role=role, content=content, timestamp=ts_parsed))
            return list(reversed(msgs))
        except Exception as e:
            logger.error(f"get_conversation_history error: {e}")
            return []

    def get_session_info(self, session_id: str) -> Optional[ConversationSession]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT session_id, user_id, created_at, updated_at, message_count, metadata FROM conversations WHERE session_id = ?''', (session_id,))
                row = cursor.fetchone()
            if not row:
                return None
            sid, uid, created, updated, count, metadata = row
            from datetime import datetime as dt
            try:
                created_dt = dt.fromisoformat(created)
            except:
                created_dt = dt.strptime(created, "%Y-%m-%d %H:%M:%S")
            try:
                updated_dt = dt.fromisoformat(updated)
            except:
                updated_dt = dt.strptime(updated, "%Y-%m-%d %H:%M:%S")
            return ConversationSession(session_id=sid, user_id=uid, created_at=created_dt, updated_at=updated_dt, message_count=count, metadata=json.loads(metadata or "{}"))
        except Exception as e:
            logger.error(f"get_session_info error: {e}")
            return None
