# Agent 6 — Prescription Ingestion Agent.
# Reads prescriptions via OCR (pytesseract) for images and via the Nutrient
# Data Extraction API for uploaded PDFs, extracts medicine names and
# dosages, and converts the result into FHIR MedicationStatement resources.

import base64
import os

from langchain_groq import ChatGroq
from PIL import Image
from pydantic import BaseModel, Field
import pytesseract

from graph.state import CrossCareState
from prompts.ingestion_prompt import PRESCRIPTION_INGESTION_PROMPT
from tools.fhir_parser import extract_medicine_dosage_pairs, prescription_to_fhir_medication_statements
from tools.nutrient_tool import extract_from_pdf

llm = ChatGroq(model="qwen/qwen3.8-27b", groq_api_key=os.getenv("GROQ_API_KEY") or "gsk_placeholder")


class NormalizedPrescription(BaseModel):
    medicines: list[str] = Field(description="Cleaned, normalized generic medicine names, noise/OCR artifacts removed")
    dosages: list[str] = Field(description="Dosage strings aligned to each medicine, same order and length as medicines")
    notes: str = Field(default="", description="Any ambiguity or low-confidence extractions worth flagging")


structured_llm = llm.with_structured_output(NormalizedPrescription)


def ocr_prescription_image(image_path: str) -> str:
    """Runs Tesseract OCR over a scanned/photographed prescription image."""
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)


def run(state: CrossCareState) -> CrossCareState:
    ocr_texts = list(state.get("ocr_text", []))
    extracted_prescription_data: dict = {}

    # PDF prescriptions are parsed via the Nutrient Data Extraction API
    # instead of OCR. If the call fails or the key isn't configured,
    # extract_from_pdf() returns a "warning" and empty lists instead of
    # raising, so the pipeline continues with whatever else is available.
    pdf_base64 = state.get("prescription_pdf_base64")
    if pdf_base64:
        pdf_bytes = base64.b64decode(pdf_base64)
        extracted_prescription_data = extract_from_pdf(pdf_bytes)
        if extracted_prescription_data.get("text"):
            ocr_texts.append(extracted_prescription_data["text"])

    all_pairs = []
    for text in ocr_texts:
        all_pairs.extend(extract_medicine_dosage_pairs(text))

    # If no raw medicines/dosages were pre-supplied (e.g. from a direct API
    # submission), let the LLM normalize the OCR/Nutrient-extracted pairs.
    # Otherwise trust the pre-supplied structured input as-is.
    if all_pairs and not state.get("medicines"):
        normalized = structured_llm.invoke(
            [
                ("system", PRESCRIPTION_INGESTION_PROMPT),
                ("human", f"Raw extracted medicine/dosage pairs: {all_pairs}"),
            ]
        )
        medicines = normalized.medicines
        dosages = normalized.dosages
        ingestion_notes = normalized.notes
    else:
        medicines = state.get("medicines", [])
        dosages = state.get("dosages", [])
        ingestion_notes = "Structured medicines/dosages supplied directly; OCR/Nutrient normalization skipped."

    fhir_medications = prescription_to_fhir_medication_statements(
        state["patient_id"], medicines, dosages
    )

    return {
        **state,
        "medicines": medicines,
        "dosages": dosages,
        "fhir_medications": fhir_medications,
        "ingestion_notes": ingestion_notes,
        "extracted_prescription_data": extracted_prescription_data,
    }
