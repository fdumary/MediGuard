// Prescription input for CrossCare — manual medicine/dosage entry, or
// upload a prescription PDF (parsed via the Nutrient Data Extraction API).

import { FileText, Plus, Send, Trash2, Upload } from "lucide-react";
import { useState } from "react";
import Button from "../ui/Button.jsx";
import Card, { CardHeader } from "../ui/Card.jsx";
import { cn } from "../../lib/utils.js";

export default function PrescriptionPanel({ onSubmitManual, onSubmitPdf, loading }) {
  const [mode, setMode] = useState("manual");
  const [patientId, setPatientId] = useState("P-003");
  const [patientName, setPatientName] = useState("");
  const [doctorName, setDoctorName] = useState("");
  const [conditions, setConditions] = useState("");
  const [rows, setRows] = useState([{ medicine: "Warfarin", dosage: "5mg daily" }, { medicine: "Amiodarone", dosage: "200mg daily" }]);
  const [file, setFile] = useState(null);

  function updateRow(i, key, value) {
    setRows((r) => r.map((row, idx) => (idx === i ? { ...row, [key]: value } : row)));
  }

  function addRow() {
    setRows((r) => [...r, { medicine: "", dosage: "" }]);
  }

  function removeRow(i) {
    setRows((r) => r.filter((_, idx) => idx !== i));
  }

  function handleManualSubmit(e) {
    e.preventDefault();
    onSubmitManual({
      patient_id: patientId,
      patient_name: patientName,
      doctor_name: doctorName || "Unspecified",
      medicines: rows.map((r) => r.medicine).filter(Boolean),
      dosages: rows.map((r) => r.dosage).filter(Boolean),
      conditions: conditions.split(",").map((c) => c.trim()).filter(Boolean),
    });
  }

  function handlePdfSubmit(e) {
    e.preventDefault();
    if (!file) return;
    onSubmitPdf({ patientId, patientName, doctorName, file });
  }

  return (
    <Card>
      <CardHeader icon={FileText} title="Prescription input" subtitle="Manual entry or upload a PDF" />

      <div className="mb-4 flex gap-1 rounded-lg bg-base-850 p-1">
        {["manual", "pdf"].map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => setMode(m)}
            className={cn(
              "flex-1 rounded-md px-3 py-1.5 text-xs font-semibold transition-colors",
              mode === m ? "bg-brand-500/15 text-brand-400" : "text-base-400 hover:text-base-200"
            )}
          >
            {m === "manual" ? "Manual entry" : "Upload PDF"}
          </button>
        ))}
      </div>

      <div className="mb-3 grid grid-cols-2 gap-3">
        <div>
          <label className="label">Patient name</label>
          <input className="input" value={patientName} onChange={(e) => setPatientName(e.target.value)} placeholder="John Doe" />
        </div>
        <div>
          <label className="label">Patient ID</label>
          <input className="input" value={patientId} onChange={(e) => setPatientId(e.target.value)} required />
        </div>
      </div>
      <div className="mb-3">
        <label className="label">Doctor name</label>
        <input className="input" value={doctorName} onChange={(e) => setDoctorName(e.target.value)} placeholder="Dr. Patel" />
      </div>

      {mode === "manual" ? (
        <form onSubmit={handleManualSubmit} className="space-y-3">
          <div>
            <label className="label">Conditions</label>
            <input className="input" value={conditions} onChange={(e) => setConditions(e.target.value)} placeholder="Atrial fibrillation" />
          </div>

          <div>
            <label className="label">Medicines &amp; dosages</label>
            <div className="space-y-2">
              {rows.map((row, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    className="input"
                    placeholder="Medicine"
                    value={row.medicine}
                    onChange={(e) => updateRow(i, "medicine", e.target.value)}
                  />
                  <input
                    className="input"
                    placeholder="Dosage"
                    value={row.dosage}
                    onChange={(e) => updateRow(i, "dosage", e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => removeRow(i)}
                    className="shrink-0 rounded-lg border border-base-700 px-2 text-base-500 hover:border-red-500/40 hover:text-red-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
            <button type="button" onClick={addRow} className="btn-ghost mt-2 text-xs">
              <Plus className="h-3.5 w-3.5" /> Add medicine
            </button>
          </div>

          <Button type="submit" icon={Send} loading={loading} className="w-full">
            Run CrossCare pipeline
          </Button>
        </form>
      ) : (
        <form onSubmit={handlePdfSubmit} className="space-y-3">
          <label
            htmlFor="prescription-pdf"
            className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-base-700 bg-base-850/40 px-4 py-8 text-center hover:border-brand-500/40"
          >
            <Upload className="h-6 w-6 text-base-500" />
            <span className="text-sm text-base-300">{file ? file.name : "Click to choose a prescription PDF"}</span>
            <span className="text-xs text-base-600">Parsed via Nutrient's Data Extraction API</span>
          </label>
          <input
            id="prescription-pdf"
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          <Button type="submit" icon={Send} loading={loading} disabled={!file} className="w-full">
            Upload &amp; run CrossCare pipeline
          </Button>
        </form>
      )}
    </Card>
  );
}
