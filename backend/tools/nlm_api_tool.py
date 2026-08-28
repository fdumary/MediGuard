# Wraps the National Library of Medicine (NLM) RxTerms/Drug Interaction API,
# used by the Pharmaco-Genomic Agent to validate antibiotic choices and dosages.

import os
import requests

NLM_API_KEY = os.getenv("NLM_API_KEY", "")
NLM_BASE_URL = "https://rxnav.nlm.nih.gov/REST"


def check_drug_interactions(rxcui_list: list[str]) -> dict:
    """
    Calls the NLM Interaction API for a list of RxCUI drug identifiers and
    returns any known interaction pairs. Falls back to an empty result set
    if the API is unreachable so the agent pipeline can continue gracefully.
    """
    try:
        response = requests.get(
            f"{NLM_BASE_URL}/interaction/list.json",
            params={"rxcuis": "+".join(rxcui_list)},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"error": str(exc), "fullInteractionTypeGroup": []}


def find_rxcui_by_name(drug_name: str) -> str | None:
    """Resolves a free-text drug name to its RxCUI identifier via NLM."""
    try:
        response = requests.get(
            f"{NLM_BASE_URL}/rxcui.json",
            params={"name": drug_name},
            timeout=10,
        )
        response.raise_for_status()
        ids = response.json().get("idGroup", {}).get("rxnormId", [])
        return ids[0] if ids else None
    except requests.RequestException:
        return None
