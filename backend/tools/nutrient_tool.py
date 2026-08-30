# Wraps the Nutrient DWS (Document Web Services) API — sponsor API for the
# API Cloud AI Hackathon 2026. Two separate products, two separate API keys:
#
#   1. Data Extraction API — POST /extraction/parse
#      Auth: NUTRIENT_EXTRACTION_API_KEY
#      Used by the Prescription Ingestion Agent to pull medicine names,
#      dosages, and patient details out of an uploaded prescription PDF.
#
#   2. Processor API — POST /build (PDF generation) and POST /sign (signing)
#      Auth: NUTRIENT_PROCESSOR_API_KEY
#      Used by the Safety Auditor Agent to render + digitally sign the
#      treatment plan audit PDF, and by the Physician Recommendation Agent
#      to render the drug interaction report PDF.
#
# Both endpoints below are now verified LIVE (2026-08-29) with real
# processor/extraction keys, real 200 OK responses, and real output:
#   - /extraction/parse: 200 OK, correctly parsed medicine/dosage lines
#   - /build (HTML -> PDF): 200 OK, valid PDF returned
#   - /sign: 200 OK — NOT a "sign" action inside /build's instructions
#     (that 400s: "`sign` is not a supported action type"); it's the
#     dedicated /sign endpoint, confirmed against the official
#     nutrient-dws Python client source.
# /data-extraction (as opposed to /extraction/parse) was requested at one
# point but verified to 404 — it does not exist on api.nutrient.io.
#
# Keys are read from the environment only — never hardcode a key here. See
# backend/.env.example for the variable names.

import base64
import json
import os

import requests

from tools.fhir_parser import extract_medicine_dosage_pairs

NUTRIENT_BASE_URL = os.getenv("NUTRIENT_BASE_URL", "https://api.nutrient.io").rstrip("/")
PROCESSOR_KEY = os.getenv("NUTRIENT_PROCESSOR_API_KEY")
EXTRACTION_KEY = os.getenv("NUTRIENT_EXTRACTION_API_KEY")


def is_extraction_configured() -> bool:
    return bool(EXTRACTION_KEY)


def is_processor_configured() -> bool:
    return bool(PROCESSOR_KEY)


def _extraction_headers() -> dict:
    return {"Authorization": f"Bearer {EXTRACTION_KEY}"}


def _processor_headers() -> dict:
    return {"Authorization": f"Bearer {PROCESSOR_KEY}"}


def _flatten_text(node) -> str:
    """Walks a nested extraction response defensively and joins every text fragment found."""
    fragments: list[str] = []

    def _walk(n):
        if isinstance(n, dict):
            text = n.get("text")
            if isinstance(text, str):
                fragments.append(text)
            for value in n.values():
                _walk(value)
        elif isinstance(n, list):
            for item in n:
                _walk(item)

    _walk(node)
    return "\n".join(fragments)


def _extract_patient_name(text: str) -> str:
    """Best-effort heuristic pull of a 'Patient: <name>' style line from extracted text."""
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("patient:"):
            return line.split(":", 1)[1].strip()
    return ""


def extract_from_pdf(file_bytes: bytes, filename: str = "prescription.pdf") -> dict:
    """
    Data Extraction API — POST /extraction/parse, authenticated with
    NUTRIENT_EXTRACTION_API_KEY (separate from the Processor API key).
    Extracts text/structured content from an uploaded prescription PDF and
    derives medicine names, dosages, and patient details from it.

    Never raises: on any failure (unconfigured key, network error, non-2xx
    response) returns a dict with a "warning" key so the calling agent can
    continue the pipeline with whatever data it already has.
    """
    if not is_extraction_configured():
        return {"warning": "NUTRIENT_EXTRACTION_API_KEY not configured", "text": "", "medicines": [], "dosages": [], "patient_name": ""}

    try:
        response = requests.post(
            f"{NUTRIENT_BASE_URL}/extraction/parse",
            headers=_extraction_headers(),
            files={"file": (filename, file_bytes, "application/pdf")},
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json()
    except requests.RequestException as exc:
        return {"warning": f"Nutrient extraction failed: {exc}", "text": "", "medicines": [], "dosages": [], "patient_name": ""}

    text = _flatten_text(raw)
    pairs = extract_medicine_dosage_pairs(text)

    return {
        "raw": raw,
        "text": text,
        "medicines": [p["medicine"] for p in pairs],
        "dosages": [p["dosage"] for p in pairs],
        "patient_name": _extract_patient_name(text),
    }


def generate_pdf(html_content: str) -> str | None:
    """
    Processor API — POST /build (HTML -> PDF), authenticated with
    NUTRIENT_PROCESSOR_API_KEY (separate from the Extraction API key).
    Renders an HTML report (e.g. a treatment plan or drug interaction
    report) into a PDF. Returns the PDF as a base64 string, or None if
    unconfigured or the call failed.
    """
    if not is_processor_configured():
        return None

    instructions = {"parts": [{"html": "content"}]}
    try:
        response = requests.post(
            f"{NUTRIENT_BASE_URL}/build",
            headers=_processor_headers(),
            files={"content": ("report.html", html_content.encode("utf-8"), "text/html")},
            data={"instructions": json.dumps(instructions)},
            timeout=30,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except requests.RequestException:
        return None


def sign_pdf(pdf_base64: str) -> str | None:
    """
    Processor API's digital signing endpoint — POST /sign, authenticated
    with NUTRIENT_PROCESSOR_API_KEY. Takes an existing PDF (base64, e.g.
    from generate_pdf()) and returns the digitally signed PDF as base64,
    or None if unconfigured or the call failed.

    VERIFIED LIVE (2026-08-29): signing is NOT a "sign" action inside
    /build's instructions — that returns a 400 ("`sign` is not a supported
    action type"). It's the dedicated /sign endpoint instead, confirmed
    against the official nutrient-dws Python client source and by a live
    200 OK response: multipart fields "file" (the PDF) + "data" (a JSON
    signature-config object; {} applies Nutrient's default signature).
    """
    if not is_processor_configured():
        return None

    pdf_bytes = base64.b64decode(pdf_base64)
    try:
        response = requests.post(
            f"{NUTRIENT_BASE_URL}/sign",
            headers=_processor_headers(),
            files={"file": ("document.pdf", pdf_bytes, "application/pdf")},
            data={"data": json.dumps({})},
            timeout=30,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode()
    except requests.RequestException:
        return None
