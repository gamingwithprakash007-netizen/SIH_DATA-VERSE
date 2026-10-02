"""
DATA VERSE: SQLite Database & Audit Persistence Engine
Module: backend.database.db

Manages relational tables and persistent audit trail for documents, signatures,
quantum sessions, measurement histograms, verification results, and attack events.
"""
import sqlite3
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.core.config import settings

def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    import tempfile
    primary_path = db_path or settings.DATABASE_PATH
    
    candidates = [
        primary_path,
        os.path.join(settings.BASE_DIR, "data", "data_verse.db"),
        os.path.join(tempfile.gettempdir(), "data_verse.db"),
        ":memory:"
    ]
    
    for c_path in candidates:
        if c_path == ":memory:":
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            return conn
            
        try:
            abs_p = os.path.abspath(c_path)
            d = os.path.dirname(abs_p)
            if d:
                os.makedirs(d, exist_ok=True)
            conn = sqlite3.connect(abs_p)
            # Quick check query to ensure file is accessible and writable
            conn.execute("CREATE TABLE IF NOT EXISTS _health_check (id INTEGER PRIMARY KEY)")
            conn.commit()
            conn.row_factory = sqlite3.Row
            return conn
        except (sqlite3.OperationalError, PermissionError, OSError):
            continue
            
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn

def init_database(db_path: Optional[str] = None) -> None:
    """Creates the 9 required SQLite tables as defined in Section 34."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 1. users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL DEFAULT 'researcher',
        created_at TEXT NOT NULL
    );
    """)

    # 2. documents
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        sha3_256 TEXT NOT NULL,
        byte_size INTEGER NOT NULL,
        file_path TEXT,
        uploaded_at TEXT NOT NULL
    );
    """)

    # 3. signatures
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS signatures (
        signature_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        signature_b64 TEXT NOT NULL,
        signature_algorithm TEXT NOT NULL,
        public_key_pem TEXT NOT NULL,
        session_id TEXT NOT NULL,
        nonce TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES documents(document_id)
    );
    """)

    # 4. quantum_sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quantum_sessions (
        session_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        protocol TEXT NOT NULL,
        bell_state TEXT NOT NULL,
        num_qubits INTEGER NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    # 5. quantum_measurements
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quantum_measurements (
        measurement_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        shots INTEGER NOT NULL,
        observed_counts_json TEXT NOT NULL,
        probabilities_json TEXT NOT NULL,
        correlation_deviation REAL NOT NULL,
        noise_level REAL NOT NULL,
        measured_at TEXT NOT NULL
    );
    """)

    # 6. verification_results
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_results (
        verification_id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        threat_score REAL NOT NULL,
        classification TEXT NOT NULL,
        verdict TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        raw_result_json TEXT NOT NULL
    );
    """)

    # 7. attack_events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attack_events (
        event_id TEXT PRIMARY KEY,
        verification_id TEXT NOT NULL,
        attack_type TEXT NOT NULL,
        detected INTEGER NOT NULL,
        threat_score REAL NOT NULL,
        details_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # 8. audit_logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id TEXT PRIMARY KEY,
        event TEXT NOT NULL,
        operation TEXT NOT NULL,
        verification_id TEXT,
        session_id TEXT,
        details_json TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # 9. system_config
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_config (
        config_key TEXT PRIMARY KEY,
        config_value TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Seed default system configs if empty
    cursor.execute("SELECT COUNT(*) FROM system_config")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("INSERT INTO system_config VALUES (?, ?, ?)", ("DEFAULT_SHOTS", str(settings.DEFAULT_SHOTS), now))
        cursor.execute("INSERT INTO system_config VALUES (?, ?, ?)", ("MAX_QUBITS", str(settings.MAX_QUBITS), now))
        cursor.execute("INSERT INTO system_config VALUES (?, ?, ?)", ("SAFE_THRESHOLD", str(settings.THREAT_THRESHOLD_SAFE), now))
        cursor.execute("INSERT INTO system_config VALUES (?, ?, ?)", ("ATTACK_THRESHOLD", str(settings.THREAT_THRESHOLD_ATTACK), now))

    conn.commit()
    conn.close()

def save_document_record(doc_data: Dict[str, Any], file_path: str = "") -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO documents (document_id, filename, sha256, sha3_256, byte_size, file_path, uploaded_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        doc_data["document_id"],
        doc_data["filename"],
        doc_data["sha256"],
        doc_data["sha3_256"],
        doc_data["size_bytes"],
        file_path,
        doc_data["timestamp"]
    ))
    conn.commit()
    conn.close()

def save_verification_record(res: Dict[str, Any]) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO verification_results 
    (verification_id, document_id, timestamp, threat_score, classification, verdict, attack_type, raw_result_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        res["verification_id"],
        res["document"]["document_id"],
        res["timestamp"],
        res["threat_evaluation"]["threat_score"],
        res["final_classification"],
        res["final_verdict"],
        res["attack_context"]["attack_simulated"],
        json.dumps(res)
    ))
    conn.commit()
    conn.close()

def list_verification_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT verification_id, document_id, timestamp, threat_score, classification, verdict, attack_type
    FROM verification_results
    ORDER BY timestamp DESC
    LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    history = [dict(r) for r in rows]
    conn.close()
    return history

def get_verification_by_id(ver_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT raw_result_json FROM verification_results WHERE verification_id = ?", (ver_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None
