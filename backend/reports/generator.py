"""
DATA VERSE: Forensic Verification Report Generator
Module: backend.reports.generator

Generates comprehensive verification reports matching the schema in Section 33.
Supports JSON export, Markdown/Plain Text export, and PDF generation via ReportLab.
"""
from typing import Dict, Any
import os
import json
from datetime import datetime, timezone
# Optional ReportLab imports handled dynamically in export_pdf_report

from backend.core.config import settings

def generate_text_report(v: Dict[str, Any]) -> str:
    """Generates structured explainable ASCII/Markdown forensic report."""
    doc = v["document"]
    sig = v["digital_signature"]
    q = v["quantum_verification"]
    t = v["threat_evaluation"]
    s = v["session_security"]
    stats = q.get("statistical_metrics", {})

    lines = [
        "============================================================",
        "DATA VERSE: Quantum-Information Digital Signature Forensic Report",
        "============================================================",
        f"Verification ID : {v['verification_id']}",
        f"Timestamp       : {v['timestamp']}",
        f"Classification  : {v['final_classification']}",
        f"Verdict         : {v['final_verdict']}",
        f"Threat Score    : {t['threat_score']} / 100.0",
        "",
        "--- DOCUMENT INTEGRITY ---",
        f"Filename        : {doc['filename']}",
        f"Document ID     : {doc['document_id']}",
        f"Size (Bytes)    : {doc['byte_size']}",
        f"Hash Algorithm  : {doc['hash_algorithm']}",
        f"Expected Hash   : {doc['expected_hash']}",
        f"Computed Hash   : {doc['computed_hash']}",
        f"Hash Status     : {'PASSED' if doc['hash_valid'] else 'FAILED'}",
        "",
        "--- DIGITAL SIGNATURE (CLASSICAL BASELINE) ---",
        f"Algorithm       : {sig['algorithm']}",
        f"Signature Status: {'VALID' if sig['signature_valid'] else 'INVALID'}",
        "",
        "--- QUANTUM VERIFICATION (VIRTUAL QUANTUM COMPUTER) ---",
        f"Simulator       : {q['simulator']}",
        f"Qubits          : {q['qubits_simulated']}",
        f"Bell State      : {q['bell_state']}",
        f"Shots           : {q['shots']}",
        f"Observed Corr   : {q['observed_correlation']}",
        f"Expected Corr   : {q['expected_correlation']}",
        f"Correlation Dev : {q['correlation_deviation']}",
        f"Teleport Status : {'SUCCESS' if q['teleportation_fidelity'] >= 0.9 else 'ANOMALY'}",
        f"Fidelity        : {q['teleportation_fidelity']}",
        f"Pauli Correction: {q['pauli_correction']}",
        f"TVD             : {stats.get('total_variation_distance', 'N/A')}",
        f"KL Divergence   : {stats.get('kl_divergence_bits', 'N/A')} bits",
        f"Chi-Square Stat : {stats.get('chi_square_stat', 'N/A')} (p={stats.get('p_value', 'N/A')})",
        "",
        "--- THREAT EVALUATION & CONTRIBUTING FACTORS ---",
        f"Document Integrity : {t['contributing_factors']['document_integrity']}",
        f"Signature Integrity: {t['contributing_factors']['signature_integrity']}",
        f"Quantum Anomaly    : {t['contributing_factors']['quantum_measurement']}",
        f"Session Integrity  : {t['contributing_factors']['session_integrity']}",
        f"Replay Indicator   : {t['contributing_factors']['replay_detection']}",
        "",
        "Contributing Reasons:",
    ]
    for r in t["reasons"]:
        lines.append(f"  * {r}")

    lines.extend([
        "",
        "--- AUDIT INFORMATION ---",
        f"Session ID      : {s['session_id']}",
        f"Nonce           : {s['nonce']}",
        f"Attack Context  : {v['attack_context']['attack_simulated']}",
        "============================================================"
    ])
    return "\n".join(lines)

def export_pdf_report(v: Dict[str, Any], output_path: str) -> str:
    """Generates a professional PDF forensic report using ReportLab (or fallback to plain text if not installed)."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        # Fallback to pure-Python valid PDF-1.4 generator if reportlab is not installed
        from backend.reports.clean_doc_pdf import make_pure_pdf
        txt = generate_text_report(v)
        pdf_bytes = make_pure_pdf(txt)
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        return output_path
    doc_pdf = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#002B49'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )

    story = [
        Paragraph("DATA VERSE: Quantum-Information Digital Signature Forensic Report", title_style),
        Paragraph(f"<b>Verification ID:</b> {v['verification_id']} | <b>Timestamp:</b> {v['timestamp']}", body_style),
        Spacer(1, 10)
    ]

    # Threat Badge Color
    cls_color = colors.HexColor('#16A34A') if v['final_classification'] == 'SAFE' else (
        colors.HexColor('#EAB308') if v['final_classification'] == 'SUSPICIOUS' else colors.HexColor('#DC2626')
    )

    summary_data = [
        ["Classification", v['final_classification'], "Threat Score", f"{v['threat_evaluation']['threat_score']}/100"],
        ["Verdict", v['final_verdict'], "Attack Mode", v['attack_context']['attack_simulated']]
    ]
    t_summary = Table(summary_data, colWidths=[110, 140, 110, 140])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (1, 0), (1, 0), cls_color),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # Document & Classical Signature Details
    story.append(Paragraph("1. Classical Document & Cryptographic Integrity", h2_style))
    doc_data = [
        ["Filename", v['document']['filename']],
        ["Document ID", v['document']['document_id']],
        ["Expected Hash (SHA-256)", v['document']['expected_hash']],
        ["Computed Hash", v['document']['computed_hash']],
        ["Hash Match Status", "PASSED" if v['document']['hash_valid'] else "FAILED (TAMPERED)"],
        ["Digital Signature (ECDSA)", "VALID" if v['digital_signature']['signature_valid'] else "FAILED"],
        ["Replay Protection", "PASSED" if not v['session_security']['replay_detected'] else "REPLAY ATTACK DETECTED"]
    ]
    t_doc = Table(doc_data, colWidths=[160, 340])
    t_doc.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_doc)
    story.append(Spacer(1, 10))

    # Quantum Verification Details
    story.append(Paragraph("2. Virtual Quantum Computer Simulation & Metrics", h2_style))
    q = v['quantum_verification']
    q_stats = q.get('statistical_metrics', {})
    q_data = [
        ["Quantum Engine", q['simulator']],
        ["Simulated Qubits / Shots", f"{q['qubits_simulated']} qubits / {q['shots']} shots"],
        ["Entangled Bell State", q['bell_state']],
        ["Observed Correlation / Expected", f"{q['observed_correlation']} / {q['expected_correlation']}"],
        ["Teleportation Fidelity", f"{q['teleportation_fidelity']:.4f}"],
        ["Total Variation Distance (TVD)", f"{q_stats.get('total_variation_distance', 'N/A')}"],
        ["Chi-Square / p-value", f"{q_stats.get('chi_square_stat', 'N/A')} (p={q_stats.get('p_value', 'N/A')})"]
    ]
    t_q = Table(q_data, colWidths=[160, 340])
    t_q.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_q)
    story.append(Spacer(1, 10))

    # Explainable Analysis
    story.append(Paragraph("3. Forensic Threat Explanation", h2_style))
    for r in v['threat_evaluation']['reasons']:
        story.append(Paragraph(f"• {r}", body_style))

    doc_pdf.build(story)
    return output_path
