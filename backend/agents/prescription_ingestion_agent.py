# Agent 6 — Prescription Ingestion Agent.
# Reads prescriptions via OCR (pytesseract), extracts medicine names and
# dosages, and converts the result into FHIR MedicationStatement resources.

import os

from langchain_groq import ChatGroq
from PIL import Image
import pytesseract

from graph.state import CrossCareState
from prompts.ingestion_prompt import PRESCRIPTION_INGESTION_PROMPT
from tools.fhir_parser import extract_medicine_dosage_pairs, prescription_to_fhir_medication_statements

llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))


def ocr_prescription_image(image_path: str) -> str:
    """Runs Tesseract OCR over a scanned/photographed prescription image."""
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


def run(state: CrossCareState) -> CrossCareState:
    ocr_texts = state.get("ocr_text", [])

    all_pairs = []
    for text in ocr_texts:
        all_pairs.extend(extract_medicine_dosage_pairs(text))

    # Let the LLM clean up / normalize noisy OCR extraction.
    response = llm.invoke(
        [
            ("system", PRESCRIPTION_INGESTION_PROMPT),
            ("human", f"Raw extracted medicine/dosage pairs: {all_pairs}"),
        ]
    )

    medicines = [pair["medicine"] for pair in all_pairs]
    dosages = [pair["dosage"] for pair in all_pairs]
    fhir_medications = prescription_to_fhir_medication_statements(
        state["patient_id"], medicines, dosages
    )

    return {
        **state,
        "medicines": medicines,
        "dosages": dosages,
        "fhir_medications": fhir_medications,
        "ingestion_notes": response.content,
    }
