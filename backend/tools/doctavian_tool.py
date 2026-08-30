# Wraps the Doctavian API — sponsor API for the API Cloud AI Hackathon 2026.
# Used by the Physician Recommendation Agent to generate a structured,
# signed document containing the drug interaction report and the safe
# alternative medicines recommended for the patient.
#
# STATUS (2026-08-30): a demo API key (DOCTAVIAN_API_KEY) and base URL
# (DOCTAVIAN_BASE_URL) have been issued, but no documentation, OpenAPI
# spec, or example request was available. Live probing of
# https://demo.api.doctavian.com confirmed a real, reachable Azure API
# Management gateway, but every guessed path (/, /docs, /swagger,
# /openapi.json, /reports, /generate-report, /sign, /documents/generate,
# and others, both GET and POST) returned the gateway's generic
# "OperationNotFound" 404 — meaning none of them match a real route.
#
# Rather than repeat the earlier mistake of shipping a guessed endpoint
# that turns out wrong, generate_drug_interaction_document() below is
# wired to real config (is_configured() reads the real key) but the
# request itself is a placeholder pending the actual endpoint path and
# payload shape from Doctavian. Update DOCUMENT_ENDPOINT_PATH and the
# payload once that's known — everything else (agent wiring, graceful
# fallback) already works.

import os

import requests

DOCTAVIAN_BASE_URL = os.getenv("DOCTAVIAN_BASE_URL", "https://api.doctavian.com/v1").rstrip("/")
DOCTAVIAN_API_KEY = os.getenv("DOCTAVIAN_API_KEY", "")

# TODO: confirm against real Doctavian docs — currently unverified.
DOCUMENT_ENDPOINT_PATH = "/documents/drug-interaction-report"


def is_configured() -> bool:
    return bool(DOCTAVIAN_API_KEY)


def generate_drug_interaction_document(
    patient_id: str,
    dangerous_combinations: list[str],
    recommendations: list[str],
    clinical_note: str,
) -> dict:
    """
    Sends CrossCare's drug interaction findings to Doctavian to generate a
    signed, structured document for the patient's chart. Returns a dict
    describing the generated document (or its status) — never raises, so
    an unverified/broken sponsor endpoint can't take down the pipeline.
    """
    if not is_configured():
        return {
            "status": "not_configured",
            "message": "DOCTAVIAN_API_KEY is not set",
        }

    payload = {
        "patient_id": patient_id,
        "dangerous_combinations": dangerous_combinations,
        "recommendations": recommendations,
        "clinical_note": clinical_note,
    }
    try:
        response = requests.post(
            f"{DOCTAVIAN_BASE_URL}{DOCUMENT_ENDPOINT_PATH}",
            json=payload,
            headers={"Authorization": f"Bearer {DOCTAVIAN_API_KEY}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"status": "error", "message": str(exc)}
