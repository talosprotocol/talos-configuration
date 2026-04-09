from talos_contracts import derive_cursor, decode_cursor
from datetime import datetime
from typing import Optional, Tuple
from src.core.storage import IdempotencyRecord
import hashlib

def encode_cursor(created_at: datetime, id: str) -> str:
    # Format: base64url(utf8("{timestamp}:{id}"))
    ts = int(created_at.timestamp())
    return derive_cursor(ts, id)

def decode_cursor_to_dt(cursor: str) -> Tuple[datetime, str]:
    try:
        decoded = decode_cursor(cursor)
        dt = datetime.fromtimestamp(decoded["timestamp"])
        return dt, decoded["event_id"]
    except Exception:
        raise ValueError("Invalid cursor")

def check_idempotency_conflict(record: IdempotencyRecord, current_digest: str) -> bool:
    """
    Returns True if there is a conflict (same key, different body).
    Returns False if it is a valid replay (same key, same body).
    """
    return record.request_digest != current_digest

def compute_body_digest(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()
