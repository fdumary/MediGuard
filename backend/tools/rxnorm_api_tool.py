# Wraps the RxNorm API, used by the Pharmacology Interaction Agent in CrossCare
# to cross-check every drug on a patient's multi-doctor prescription list.

import requests

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"


def get_drug_details(drug_name: str) -> dict:
    """Fetches RxNorm properties (RxCUI, ingredient, dose form) for a drug name."""
    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/drugs.json",
            params={"name": drug_name},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc)}


def check_interaction_pair(rxcui_a: str, rxcui_b: str) -> dict:
    """Checks a pairwise interaction between two RxCUI drug identifiers."""
    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/interaction/list.json",
            params={"rxcuis": f"{rxcui_a}+{rxcui_b}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc), "fullInteractionTypeGroup": []}


def find_alternatives(rxcui: str) -> list[str]:
    """Suggests related/alternative drugs in the same therapeutic class via RxNorm."""
    try:
        response = requests.get(
            f"{RXNORM_BASE_URL}/rxcui/{rxcui}/related.json",
            params={"tty": "SCD+SBD"},
            timeout=10,
        )
        response.raise_for_status()
        groups = response.json().get("relatedGroup", {}).get("conceptGroup", [])
        names = []
        for group in groups:
            for concept in group.get("conceptProperties", []):
                names.append(concept.get("name"))
        return names
    except requests.RequestException:
        return []
