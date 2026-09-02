# Tests for the Doctavian tool wrapper's graceful-degradation behavior.
# Doctavian's real endpoint path is still unverified (see module docstring
# in tools/doctavian_tool.py), so these only test the not-configured path
# and the never-raises contract, not a live call.

from tools import doctavian_tool


def test_not_configured_returns_status_dict(monkeypatch):
    monkeypatch.setattr(doctavian_tool, "DOCTAVIAN_API_KEY", "")
    result = doctavian_tool.generate_drug_interaction_document(
        patient_id="P-003",
        dangerous_combinations=["Warfarin + Amiodarone"],
        recommendations=["Reduce warfarin dose"],
        clinical_note="Test note",
    )
    assert result["status"] == "not_configured"


def test_is_configured_reflects_key(monkeypatch):
    monkeypatch.setattr(doctavian_tool, "DOCTAVIAN_API_KEY", "")
    assert doctavian_tool.is_configured() is False
    monkeypatch.setattr(doctavian_tool, "DOCTAVIAN_API_KEY", "some-key")
    assert doctavian_tool.is_configured() is True
