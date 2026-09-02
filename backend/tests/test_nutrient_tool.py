# Tests for the Nutrient DWS tool wrapper's pure-logic pieces and its
# graceful-degradation behavior when unconfigured. Does NOT call the real
# API (that's verified manually against live keys — see project history).

from tools import nutrient_tool


def test_flatten_extracted_text_walks_nested_structure():
    sample = {
        "output": {
            "elements": [
                {"text": "Warfarin 5mg once daily"},
                {"text": "Aspirin 100mg once daily"},
            ]
        }
    }
    result = nutrient_tool._flatten_text(sample)
    assert "Warfarin 5mg once daily" in result
    assert "Aspirin 100mg once daily" in result


def test_flatten_extracted_text_handles_lists_and_missing_text():
    sample = {"pages": [{"role": "Text"}, {"text": "Metformin 500mg"}]}
    assert nutrient_tool._flatten_text(sample) == "Metformin 500mg"


def test_flatten_extracted_text_empty_input():
    assert nutrient_tool._flatten_text({}) == ""
    assert nutrient_tool._flatten_text([]) == ""


def test_extraction_unconfigured_returns_warning_not_raise(monkeypatch):
    monkeypatch.setattr(nutrient_tool, "EXTRACTION_KEY", "")
    result = nutrient_tool.extract_from_pdf(b"%PDF-1.4 fake", "test.pdf")
    assert "warning" in result
    assert result["medicines"] == []
    assert result["dosages"] == []


def test_generate_pdf_unconfigured_returns_none(monkeypatch):
    monkeypatch.setattr(nutrient_tool, "PROCESSOR_KEY", "")
    assert nutrient_tool.generate_pdf("<h1>test</h1>") is None


def test_sign_pdf_unconfigured_returns_none(monkeypatch):
    monkeypatch.setattr(nutrient_tool, "PROCESSOR_KEY", "")
    assert nutrient_tool.sign_pdf("aGVsbG8=") is None


def test_is_extraction_configured_reflects_key(monkeypatch):
    monkeypatch.setattr(nutrient_tool, "EXTRACTION_KEY", "")
    assert nutrient_tool.is_extraction_configured() is False
    monkeypatch.setattr(nutrient_tool, "EXTRACTION_KEY", "some-key")
    assert nutrient_tool.is_extraction_configured() is True


def test_is_processor_configured_reflects_key(monkeypatch):
    monkeypatch.setattr(nutrient_tool, "PROCESSOR_KEY", "")
    assert nutrient_tool.is_processor_configured() is False
    monkeypatch.setattr(nutrient_tool, "PROCESSOR_KEY", "some-key")
    assert nutrient_tool.is_processor_configured() is True
