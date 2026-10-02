import tempfile
"""
DATA VERSE: FastAPI REST API Engine
Module: backend.api.app

Exposes full platform functionality via REST endpoints:
- Document Upload and Cryptographic Fingerprinting
- Classical and Quantum Digital Signature Generation
- Forensic Verification Pipeline
- Quantum State & Circuit Simulation (Gates, Bell States, Teleportation)
- Controlled Cyber Attack Laboratory
- Verification History and Audit Ledger
- Forensic Report Retrieval and PDF Export
- System Configuration and Health
"""
import os
import sys
import json
import uuid
import base64
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse, Response
from pydantic import BaseModel, Field

from backend.core.config import settings
from backend.crypto.hashing import compute_document_hashes
from backend.crypto.signatures import KeyManager
from backend.qds.protocol import sign_document_qds, SignaturePackage
from backend.quantum.circuit import QuantumCircuit
from backend.quantum.bell import analyze_bell_correlations, BELL_STATES
from backend.quantum.teleportation import run_quantum_teleportation
from backend.quantum.validation import run_cross_validation_suite
from backend.verification.engine import run_verification_pipeline
from backend.attacks.lab import AttackLab
from backend.reports.generator import generate_text_report, export_pdf_report
from backend.database.db import (
    init_database,
    save_document_record,
    save_verification_record,
    list_verification_history,
    get_verification_by_id,
    get_connection
)

# Initialize database on startup
init_database()

app = FastAPI(
    title="DATA VERSE API",
    description="Quantum-Information-Based Digital Signature Security & Threat Detection Platform (SIH26141)",
    version="1.0.0-research-prototype"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory document storage for uploaded raw bytes
DOCUMENT_STORE: Dict[str, bytes] = {}
SIGNATURE_STORE: Dict[str, Dict[str, Any]] = {}

# --- PDF GENERATION & EXTRACTION (FAIL-SAFE ARCHITECTURE) ---
try:
    from backend.reports.clean_doc_pdf import (
        build_clean_document_pdf_bytes,
        generate_clean_document_pdf,
        make_pure_pdf,
        extract_qds_from_pdf,
        embed_qds_metadata_in_pdf
    )
except ImportError:
    import json
    from backend.crypto.hashing import extract_document_text

    def make_pure_pdf(text_content: str, metadata_dict: Optional[Dict[str, Any]] = None) -> bytes:
        raw_text = text_content or ""
        lines = raw_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        stream_lines = ['BT', '/F1 11 Tf', '50 740 Td', '14 TL']
        for l in lines:
            safe_line = l.replace('\\', '\\\\').replace('(', '\(').replace(')', '\)')
            stream_lines.append(f'({safe_line}) Tj')
            stream_lines.append('T*')
        stream_lines.append('ET')
        stream_data = '\n'.join(stream_lines).encode('latin-1', errors='replace')
        meta_json = json.dumps(metadata_dict) if metadata_dict else '{}'
        safe_meta = meta_json.replace('\\', '\\\\').replace('(', '\(').replace(')', '\)')
        meta_bytes = f'QDS_PACKAGE:{safe_meta}'.encode('latin-1', errors='replace')
        
        obj1 = b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        obj2 = b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        obj3 = b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n'
        obj4 = b'4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n'
        obj5 = f'5 0 obj\n<< /Length {len(stream_data)} >>\nstream\n'.encode('latin-1') + stream_data + b'\nendstream\nendobj\n'
        obj6 = b'6 0 obj\n<< /Title (Clean Document) /Keywords (' + meta_bytes + b') >>\nendobj\n'
        header = b'%PDF-1.4\n'
        pos1, pos2, pos3 = len(header), len(header) + len(obj1), len(header) + len(obj1) + len(obj2)
        pos4 = pos3 + len(obj3)
        pos5 = pos4 + len(obj4)
        pos6 = pos5 + len(obj5)
        xref_pos = pos6 + len(obj6)
        xref = f'xref\n0 7\n0000000000 65535 f \n{pos1:010d} 00000 n \n{pos2:010d} 00000 n \n{pos3:010d} 00000 n \n{pos4:010d} 00000 n \n{pos5:010d} 00000 n \n{pos6:010d} 00000 n \ntrailer\n<< /Size 7 /Root 1 0 R /Info 6 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n'.encode('latin-1')
        return header + obj1 + obj2 + obj3 + obj4 + obj5 + obj6 + xref

    def embed_qds_metadata_in_pdf(pdf_bytes: bytes, metadata_dict: Dict[str, Any]) -> bytes:
        meta_json = json.dumps(metadata_dict)
        try:
            import pypdf, io
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            writer = pypdf.PdfWriter()
            writer.append(reader)
            writer.add_metadata({"/Keywords": "QDS_PACKAGE:" + meta_json})
            out_buf = io.BytesIO()
            writer.write(out_buf)
            return out_buf.getvalue()
        except Exception:
            return pdf_bytes + b"\n%QDS_PACKAGE:" + meta_json.encode("utf-8") + b"\n"

    def extract_qds_from_pdf(pdf_bytes: bytes) -> Optional[Dict[str, Any]]:
        try:
            import pypdf, io
            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            if reader.metadata:
                for v in reader.metadata.values():
                    if 'QDS_PACKAGE:' in str(v or ''):
                        return json.loads(str(v).split('QDS_PACKAGE:', 1)[1].rstrip(')\n\r'))
        except Exception:
            pass
        idx = pdf_bytes.find(b'QDS_PACKAGE:')
        if idx != -1:
            chunk = pdf_bytes[idx + len(b'QDS_PACKAGE:'):]
            s = chunk.find(b'{')
            if s != -1:
                depth = 0
                for i, b in enumerate(chunk[s:]):
                    if b == ord('{'): depth += 1
                    elif b == ord('}'):
                        depth -= 1
                        if depth == 0:
                            return json.loads(chunk[s:s+i+1].decode('utf-8', errors='replace'))
        return None

    def build_clean_document_pdf_bytes(content_bytes: bytes, filename: str, qds_metadata: Optional[Dict[str, Any]] = None) -> bytes:
        if content_bytes.startswith(b'%PDF'):
            return embed_qds_metadata_in_pdf(content_bytes, qds_metadata) if qds_metadata else content_bytes
        text = extract_document_text(content_bytes, filename=filename) or content_bytes.decode('utf-8', errors='replace')
        return make_pure_pdf(text, metadata_dict=qds_metadata)

    def generate_clean_document_pdf(content_bytes: bytes, filename: str, output_path: str, qds_metadata: Optional[Dict[str, Any]] = None) -> str:
        pdf_bytes = build_clean_document_pdf_bytes(content_bytes, filename=filename, qds_metadata=qds_metadata)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        return output_path


# Pydantic Schemas
class GateInput(BaseModel):
    name: str
    qubits: List[int]
    params: Optional[List[float]] = []

class CircuitRunRequest(BaseModel):
    num_qubits: int = Field(2, ge=1, le=settings.MAX_QUBITS)
    gates: List[GateInput]
    shots: int = Field(settings.DEFAULT_SHOTS, ge=settings.MIN_SHOTS, le=settings.MAX_SHOTS)
    seed: Optional[int] = None

class BellStateRequest(BaseModel):
    state_name: str = "phi_plus"
    shots: int = Field(settings.DEFAULT_SHOTS, ge=settings.MIN_SHOTS, le=settings.MAX_SHOTS)
    seed: Optional[int] = None

class TeleportationRequest(BaseModel):
    alpha: float = 0.70710678
    beta: float = 0.70710678
    seed: Optional[int] = None

class SignDocumentRequest(BaseModel):
    document_id: str
    shots: int = Field(1024, ge=100, le=10000)
    seed: Optional[int] = None

class VerifyRequest(BaseModel):
    document_id: str
    signature_package: Dict[str, Any]
    check_replay: bool = True

class TamperAttackRequest(BaseModel):
    document_id: str
    signature_package: Dict[str, Any]
    tamper_offset: int = 10

class NoiseAttackRequest(BaseModel):
    document_id: str
    signature_package: Dict[str, Any]
    depolarizing_prob: float = 0.25

# --- SYSTEM & STATUS ENDPOINTS ---
@app.get("/system/status")
def get_system_status():
    return {
        "status": "OPERATIONAL",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "sih_problem": settings.SIH_PROBLEM,
        "quantum_simulator": "DATA VERSE Virtual Quantum Computer (NumPy Backend)",
        "classical_crypto": "ECDSA (SECP256R1), SHA-256, SHA3-256",
        "max_qubits_supported": settings.MAX_QUBITS,
        "default_shots": settings.DEFAULT_SHOTS,
        "threat_thresholds": {
            "safe": settings.THREAT_THRESHOLD_SAFE,
            "attack": settings.THREAT_THRESHOLD_ATTACK
        },
        "storage": {
            "database_path": settings.DATABASE_PATH,
            "documents_cached": len(DOCUMENT_STORE)
        }
    }

@app.get("/quantum/info")
def get_quantum_info():
    return {
        "architecture": "Pure State Vector Engine with Born Rule Measurement",
        "supported_single_qubit_gates": ["X", "Y", "Z", "H", "S", "T", "S_DAG", "T_DAG", "RX", "RY", "RZ", "PHASE"],
        "supported_two_qubit_gates": ["CNOT", "CZ", "SWAP"],
        "canonical_bell_states": BELL_STATES,
        "protocols": ["Bell-State Correlation Analysis", "3-Qubit Quantum Teleportation with Pauli Correction"],
        "noise_channels": ["Bit-Flip", "Phase-Flip", "Depolarizing", "Readout Error"]
    }

# --- DOCUMENT & SIGNATURE ENDPOINTS ---
@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > settings.UPLOAD_LIMIT_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds maximum upload size limit (10MB).")
    
    hashes = compute_document_hashes(content, filename=file.filename)
    doc_id = hashes["document_id"]
    DOCUMENT_STORE[doc_id] = content
    
    # Persist file content to disk so server restarts do not lose uploaded documents
    file_path = ""
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception:
        file_path = ""

    save_document_record(hashes, file_path=file_path)
    return hashes

@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM documents WHERE document_id = ?", (doc_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document ID not found.")
    return dict(row)

@app.get("/documents/{doc_id}/pdf")
def download_clean_document_pdf(doc_id: str):
    """
    Downloads the signed document in clean PDF format with NO visible signature text.
    The document body remains completely pristine and detached from signature metadata.
    Completely fail-safe against missing memory cache, server restarts, and Windows file locks.
    """
    content = None
    raw_filename = None

    if doc_id in DOCUMENT_STORE:
        content = DOCUMENT_STORE[doc_id]

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT filename, file_path FROM documents WHERE document_id = ?", (doc_id,))
    row = c.fetchone()
    conn.close()

    if row:
        raw_filename = row["filename"]
        file_path = row["file_path"]
        if content is None and file_path and os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                    DOCUMENT_STORE[doc_id] = content
            except Exception:
                pass

    if content is None:
        raise HTTPException(status_code=404, detail="Document content not found. Please upload or sign the document first.")

    raw_filename = raw_filename or f"document_{doc_id[:8]}.pdf"

    
    # Fetch signature package if document was signed, to embed invisibly in the PDF metadata
    qds_meta = SIGNATURE_STORE.get(doc_id)
    
    try:
        pdf_bytes = build_clean_document_pdf_bytes(content, filename=raw_filename, qds_metadata=qds_meta)
    except Exception:
        try:
            text = content.decode("utf-8", errors="replace")
        except Exception:
            text = f"Document: {raw_filename}"
        pdf_bytes = make_pure_pdf(text, metadata_dict=qds_meta)

    clean_filename = os.path.splitext(raw_filename)[0] + ".pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{clean_filename}"'}
    )

@app.post("/sign")
def sign_document_endpoint(req: SignDocumentRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found in storage. Please upload first.")
    
    content = DOCUMENT_STORE[req.document_id]
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT filename FROM documents WHERE document_id = ?", (req.document_id,))
    row = c.fetchone()
    conn.close()
    orig_filename = row["filename"] if row else f"doc_{req.document_id[:8]}.bin"

    pkg, _ = sign_document_qds(
        content_bytes=content,
        filename=orig_filename,
        shots=req.shots,
        seed=req.seed
    )
    res_dict = pkg.to_dict()
    res_dict["document_id"] = req.document_id
    SIGNATURE_STORE[req.document_id] = res_dict
    return res_dict

@app.post("/verify")
def verify_document_endpoint(req: VerifyRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document content not found for verification.")
    
    content = DOCUMENT_STORE[req.document_id]
    result = run_verification_pipeline(
        document_bytes=content,
        signature_package_dict=req.signature_package,
        check_replay=req.check_replay
    )
    save_verification_record(result)
    return result

@app.post("/verify/independent")
async def verify_independent(
    document: UploadFile = File(...),
    signature_package: Optional[UploadFile] = File(None)
):
    """
    Verifies a signed document. Supports single-file PDF verification where the QDS package
    is extracted directly from the PDF's internal metadata, or dual-file verification.
    """
    doc_bytes = await document.read()
    
    if signature_package is not None:
        pkg_bytes = await signature_package.read()
        try:
            pkg_dict = json.loads(pkg_bytes.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid signature package JSON: {str(e)}")
    else:
        # Single-file PDF verification: extract embedded QDS package from PDF metadata
        pkg_dict = extract_qds_from_pdf(doc_bytes)
        if not pkg_dict:
            raise HTTPException(
                status_code=400,
                detail="No embedded QDS signature found in this PDF. Please ensure this document was signed using DATA VERSE."
            )
        
    result = run_verification_pipeline(
        document_bytes=doc_bytes,
        signature_package_dict=pkg_dict,
        check_replay=True,
        uploaded_filename=document.filename
    )
    save_verification_record(result)
    return result

@app.post("/verify/pdf")
async def verify_single_pdf(document: UploadFile = File(...)):
    """Dedicated single-file PDF verification endpoint."""
    return await verify_independent(document=document, signature_package=None)

# --- VIRTUAL QUANTUM COMPUTER ENDPOINTS ---
@app.post("/quantum/run")
def run_custom_circuit(req: CircuitRunRequest):
    qc = QuantumCircuit(req.num_qubits)
    for g in req.gates:
        qc.apply_gate(g.name, *g.qubits, **{f"param_{i}": p for i, p in enumerate(g.params or [])})
    res = qc.run(shots=req.shots, seed=req.seed)
    return res.to_dict()

@app.post("/quantum/bell-state")
def run_bell_state_endpoint(req: BellStateRequest):
    return analyze_bell_correlations(state_name=req.state_name, shots=req.shots, seed=req.seed)

@app.post("/quantum/teleport")
def run_teleportation_endpoint(req: TeleportationRequest):
    from backend.quantum.qubit import Qubit
    qubit = Qubit(req.alpha, req.beta)
    return run_quantum_teleportation(input_qubit=qubit, seed=req.seed)

@app.get("/quantum/validate")
def run_validation_endpoint():
    return run_cross_validation_suite()

# --- ATTACK LABORATORY ENDPOINTS ---
@app.post("/attacks/tamper")
def attack_tamper(req: TamperAttackRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_document_tampering(
        original_bytes=content,
        signature_pkg=req.signature_package,
        tamper_offset=req.tamper_offset
    )
    save_verification_record(res["verification_result"])
    return res

@app.post("/attacks/signature-tamper")
def attack_sig_tamper(req: VerifyRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_signature_tampering(
        document_bytes=content,
        signature_pkg=req.signature_package
    )
    save_verification_record(res["verification_result"])
    return res

@app.post("/attacks/forgery")
def attack_forgery(req: VerifyRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_forgery(
        document_bytes=content,
        signature_pkg=req.signature_package
    )
    save_verification_record(res["verification_result"])
    return res

@app.post("/attacks/replay")
def attack_replay(req: VerifyRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_replay_attack(
        document_bytes=content,
        signature_pkg=req.signature_package
    )
    save_verification_record(res["verification_result"])
    return res

@app.post("/attacks/noise")
def attack_noise(req: NoiseAttackRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_quantum_noise(
        document_bytes=content,
        signature_pkg=req.signature_package,
        depolarizing_prob=req.depolarizing_prob
    )
    save_verification_record(res["verification_result"])
    return res

@app.post("/attacks/measurement-manipulation")
def attack_manipulation(req: VerifyRequest):
    if req.document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found.")
    content = DOCUMENT_STORE[req.document_id]
    res = AttackLab.simulate_measurement_manipulation(
        document_bytes=content,
        signature_pkg=req.signature_package
    )
    save_verification_record(res["verification_result"])
    return res

# --- HISTORY & REPORTS ---
@app.get("/history")
def get_history(limit: int = 50):
    return list_verification_history(limit=limit)

@app.get("/verification/{ver_id}")
def get_verification(ver_id: str):
    res = get_verification_by_id(ver_id)
    if not res:
        raise HTTPException(status_code=404, detail="Verification result not found.")
    return res

@app.get("/reports/{ver_id}")
def get_report_text(ver_id: str):
    res = get_verification_by_id(ver_id)
    if not res:
        raise HTTPException(status_code=404, detail="Verification result not found.")
    return {"text_report": generate_text_report(res), "structured": res}

@app.get("/reports/{ver_id}/pdf")
def get_report_pdf(ver_id: str):
    res = get_verification_by_id(ver_id)
    if not res:
        raise HTTPException(status_code=404, detail="Verification result not found.")
    try:
        import reportlab
        report_path = os.path.join(tempfile.gettempdir(), f"report_{ver_id}.pdf")
        export_pdf_report(res, report_path)
        return FileResponse(report_path, media_type="application/pdf", filename=f"forensic_report_{ver_id}.pdf")
    except ImportError:
        report_path = os.path.join(tempfile.gettempdir(), f"report_{ver_id}.txt")
        export_pdf_report(res, report_path)
        return FileResponse(report_path, media_type="text/plain", filename=f"forensic_report_{ver_id}.txt")

# Mount static files and frontend UI
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>DATA VERSE API Running.</h1><p>Visit <a href='/docs'>/docs</a> for OpenAPI documentation.</p>")
