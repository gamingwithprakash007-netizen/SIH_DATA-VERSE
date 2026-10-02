"""
DATA VERSE: Cryptographic Document Fingerprinting Engine
Module: backend.crypto.hashing

Implements document fingerprinting with standard algorithms:
- SHA-256 (FIPS 180-4)
- SHA3-256 (FIPS 202)
- Canonical Content-Preserving Text Extraction & Hashing (for cross-format verification)
"""
import hashlib
import os
import io
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

def extract_document_text(content_bytes: bytes, filename: str = "") -> Optional[str]:
    """
    Extracts text from PDF, DOCX, or text-based documents to enable cross-format verification.
    Returns None if content is raw non-text binary (e.g. image or unsupported binary).
    """
    fname_lower = filename.lower()
    
    # 1. PDF extraction (magic bytes check)
    if content_bytes.startswith(b'%PDF'):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            pages_text = [page.extract_text() or '' for page in reader.pages]
            full_text = '\n'.join(pages_text).strip()
            if full_text:
                return full_text
        except Exception:
            pass

    # 2. DOCX extraction
    if fname_lower.endswith('.docx') or content_bytes.startswith(b'PK\x03\x04'):
        try:
            import docx
            doc = docx.Document(io.BytesIO(content_bytes))
            paras = [p.text for p in doc.paragraphs if p.text]
            for t in doc.tables:
                for row in t.rows:
                    paras.extend([cell.text for cell in row.cells if cell.text])
            full_text = '\n'.join(paras).strip()
            if full_text:
                return full_text
        except Exception:
            pass

    # 3. Plaintext / Markdown / CSV / JSON
    for enc in ('utf-8', 'utf-8-sig', 'latin-1'):
        try:
            decoded = content_bytes.decode(enc)
            # Verify it looks like plausible text (printable ASCII or unicode)
            printable_ratio = sum(1 for c in decoded if c.isprintable() or c in '\r\n\t ') / max(1, len(decoded))
            if printable_ratio > 0.85:
                return decoded.strip()
        except Exception:
            continue

    return None

def normalize_text_content(text: str) -> str:
    """
    Normalizes whitespace, line breaks, and punctuation spacing to ensure consistent
    content hashing across different file formats (e.g. TXT -> PDF conversion).
    """
    if not text:
        return ""
    # Normalize CRLF and CR to LF
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [' '.join(line.split()) for line in t.split('\n')]
    clean_lines = [l for l in lines if l]
    return '\n'.join(clean_lines).strip()

def compute_canonical_content_hash(text: Optional[str]) -> Optional[str]:
    """Computes SHA-256 digest of normalized canonical text content."""
    if not text:
        return None
    normalized = normalize_text_content(text)
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

def compute_document_hashes(content_bytes: bytes, filename: str = "document.bin") -> Dict[str, Any]:
    """
    Computes cryptographic fingerprints using SHA-256 and SHA3-256,
    plus canonical content hash for cross-format integrity verification.
    """
    sha256_hash = hashlib.sha256(content_bytes).hexdigest()
    sha3_256_hash = hashlib.sha3_256(content_bytes).hexdigest()
    
    extracted_text = extract_document_text(content_bytes, filename=filename)
    canonical_hash = compute_canonical_content_hash(extracted_text)
    
    doc_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    
    # Determine format tag
    if content_bytes.startswith(b'%PDF') or filename.lower().endswith('.pdf'):
        detected_fmt = "PDF"
    elif filename.lower().endswith('.docx'):
        detected_fmt = "DOCX"
    elif extracted_text is not None:
        detected_fmt = "TEXT"
    else:
        detected_fmt = "BINARY"

    return {
        "document_id": doc_id,
        "filename": filename,
        "size_bytes": len(content_bytes),
        "sha256": sha256_hash,
        "sha3_256": sha3_256_hash,
        "canonical_content_hash": canonical_hash,
        "detected_format": detected_fmt,
        "has_canonical_text": extracted_text is not None,
        "timestamp": ts,
        "primary_hash": sha256_hash,
        "primary_algorithm": "SHA-256"
    }

def verify_document_integrity(
    content_bytes: bytes,
    expected_hash: str,
    algorithm: str = "SHA-256",
    expected_canonical_hash: Optional[str] = None,
    filename: str = ""
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Verifies that the document content matches the expected cryptographic hash.
    Supports two verification modes:
    1. Exact Byte-Level Verification (Direct binary hash match).
    2. Cross-Format Content Verification (Normalizes text from PDF, DOCX, or TXT).
    """
    algo_clean = algorithm.upper().replace("-", "")
    if "SHA3" in algo_clean:
        current_byte_hash = hashlib.sha3_256(content_bytes).hexdigest()
    else:
        current_byte_hash = hashlib.sha256(content_bytes).hexdigest()

    # Check 1: Exact byte match
    if current_byte_hash.lower() == expected_hash.lower():
        details = {
            "expected_hash": expected_hash,
            "computed_hash": current_byte_hash,
            "match_type": "EXACT_BYTE_MATCH",
            "cross_format_verified": False,
            "algorithm": algorithm,
            "match": True,
            "byte_count": len(content_bytes)
        }
        return True, current_byte_hash, details

    # Check 1b: Exact byte match with stripped invisible QDS trailer metadata
    for marker in (b'%QDS_PACKAGE:', b'\n%QDS_PACKAGE:', b'QDS_PACKAGE:'):
        if marker in content_bytes:
            idx = content_bytes.rfind(marker)
            if idx > 0:
                stripped_cand = content_bytes[:idx].rstrip(b'\r\n')
                for trial in (stripped_cand, stripped_cand + b'\n', stripped_cand + b'\r\n'):
                    if hashlib.sha256(trial).hexdigest().lower() == expected_hash.lower():
                        details = {
                            'expected_hash': expected_hash,
                            'computed_hash': expected_hash,
                            'match_type': 'EXACT_BYTE_MATCH_STRIPPED_META',
                            'cross_format_verified': False,
                            'algorithm': algorithm,
                            'match': True,
                            'byte_count': len(trial)
                        }
                        return True, expected_hash, details

    # Check 2: Cross-format canonical content match (e.g. signer signed TXT and verifier uploaded PDF)
    if expected_canonical_hash:
        extracted = extract_document_text(content_bytes, filename=filename)
        computed_canonical = compute_canonical_content_hash(extracted)
        if computed_canonical and computed_canonical.lower() == expected_canonical_hash.lower():
            details = {
                "expected_hash": expected_hash,
                "computed_hash": current_byte_hash,
                "expected_canonical_hash": expected_canonical_hash,
                "computed_canonical_hash": computed_canonical,
                "match_type": "CROSS_FORMAT_CONTENT_MATCH",
                "cross_format_verified": True,
                "algorithm": "CANONICAL-CONTENT-SHA-256",
                "match": True,
                "byte_count": len(content_bytes)
            }
            return True, current_byte_hash, details

    # Failure: Neither byte nor canonical content matched
    extracted = extract_document_text(content_bytes, filename=filename)
    computed_canonical = compute_canonical_content_hash(extracted)
    details = {
        "expected_hash": expected_hash,
        "computed_hash": current_byte_hash,
        "expected_canonical_hash": expected_canonical_hash,
        "computed_canonical_hash": computed_canonical,
        "match_type": "MISMATCH",
        "cross_format_verified": False,
        "algorithm": algorithm,
        "match": False,
        "byte_count": len(content_bytes)
    }
    return False, current_byte_hash, details

def inspect_byte_differences(original_bytes: bytes, tampered_bytes: bytes, max_diffs: int = 5) -> Dict[str, Any]:
    min_len = min(len(original_bytes), len(tampered_bytes))
    diffs = []
    
    for idx in range(min_len):
        if original_bytes[idx] != tampered_bytes[idx]:
            diffs.append({
                "byte_offset": idx,
                "original_byte": f"0x{original_bytes[idx]:02x} ('{chr(original_bytes[idx]) if 32 <= original_bytes[idx] <= 126 else '.'}')",
                "tampered_byte": f"0x{tampered_bytes[idx]:02x} ('{chr(tampered_bytes[idx]) if 32 <= tampered_bytes[idx] <= 126 else '.'}')"
            })
            if len(diffs) >= max_diffs:
                break
                
    length_mismatch = len(original_bytes) != len(tampered_bytes)
    return {
        "length_diff": len(tampered_bytes) - len(original_bytes),
        "total_diff_preview": diffs,
        "length_mismatch": length_mismatch,
        "total_diff_count": sum(1 for i in range(min_len) if original_bytes[i] != tampered_bytes[i]) + abs(len(original_bytes) - len(tampered_bytes))
    }
