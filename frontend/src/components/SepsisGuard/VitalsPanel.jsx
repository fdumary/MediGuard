// Patient quick-select + vitals input form for SepsisGuard.

import { Send, Users } from "lucide-react";
import { useEffect, useState } from "react";
import Button from "../ui/Button.jsx";
import Card, { CardHeader } from "../ui/Card.jsx";
import { getPatients } from "../../lib/api.js";

const FIELDS = [
  { key: "heart_rate", label: "Heart rate (bpm)" },
  { key: "blood_pressure_systolic", label: "BP systolic (mmHg)" },
  { key: "blood_pressure_diastolic", label: "BP diastolic (mmHg)" },
  { key: "temperature", label: "Temperature (°C)" },
  { key: "respiratory_rate", label: "Respiratory rate (/min)" },
  { key: "lactate", label: "Lactate (mmol/L)" },
  { key: "wbc_count", label: "WBC count (k/uL)" },
];

const BLANK_FORM = {
  patient_id: "",
  patient_name: "",
  heart_rate: "",
  blood_pressure_systolic: "",
  blood_pressure_diastolic: "",
  temperature: "",
  respiratory_rate: "",
  lactate: "",
  wbc_count: "",
  current_medications: "",
};

export default function VitalsPanel({ onSubmit, loading }) {
  const [patients, setPatients] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [form, setForm] = useState(BLANK_FORM);

  useEffect(() => {
    getPatients().then(setPatients).catch(() => setPatients([]));
  }, []);

  function selectPatient(patient) {
    setSelectedId(patient.patient_id);
    const [systolic, diastolic] = patient.blood_pressure.split("/");
    setForm({
      patient_id: patient.patient_id,
      patient_name: patient.name || "",
      heart_rate: String(patient.heart_rate),
      blood_pressure_systolic: systolic,
      blood_pressure_diastolic: diastolic,
      temperature: String(patient.temperature),
      respiratory_rate: String(patient.respiratory_rate),
      lactate: String(patient.lactate),
      wbc_count: String(patient.wbc_count),
      current_medications: (patient.current_medications || []).join(", "),
    });
  }

  function update(key, value) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      patient_id: form.patient_id,
      patient_name: form.patient_name,
      heart_rate: Number(form.heart_rate),
      blood_pressure_systolic: Number(form.blood_pressure_systolic),
      blood_pressure_diastolic: Number(form.blood_pressure_diastolic),
      temperature: Number(form.temperature),
      respiratory_rate: Number(form.respiratory_rate),
      lactate: Number(form.lactate),
      wbc_count: Number(form.wbc_count),
      timestamp: new Date().toISOString(),
      current_medications: form.current_medications
        .split(",")
        .map((m) => m.trim())
        .filter(Boolean),
    });
  }

  const isValid = form.patient_id && FIELDS.every((f) => form[f.key] !== "");

  return (
    <Card>
      <CardHeader icon={Users} title="Patient vitals" subtitle="Quick-select a simulated patient or enter readings manually" />

      <div className="mb-4 flex flex-wrap gap-2">
        {patients.map((p) => (
          <button
            key={p.patient_id}
            type="button"
            onClick={() => selectPatient(p)}
            className={`rounded-xl border px-3 py-2 text-left text-xs transition-colors ${
              selectedId === p.patient_id
                ? "border-brand-500/50 bg-brand-500/10 text-brand-300"
                : "border-base-700 bg-base-850 text-base-300 hover:border-base-600"
            }`}
          >
            <p className="font-semibold text-base-100">{p.name}</p>
            <p className="text-base-500">{p.patient_id} · age {p.age}</p>
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Patient name</label>
            <input
              className="input"
              value={form.patient_name}
              onChange={(e) => update("patient_name", e.target.value)}
              placeholder="Robert Chen"
            />
          </div>
          <div>
            <label className="label">Patient ID</label>
            <input
              className="input"
              value={form.patient_id}
              onChange={(e) => update("patient_id", e.target.value)}
              placeholder="P-003"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {FIELDS.map(({ key, label }) => (
            <div key={key}>
              <label className="label">{label}</label>
              <input
                className="input"
                type="number"
                step="any"
                value={form[key]}
                onChange={(e) => update(key, e.target.value)}
                required
              />
            </div>
          ))}
        </div>

        <div>
          <label className="label">Current medications (comma-separated)</label>
          <input
            className="input"
            value={form.current_medications}
            onChange={(e) => update("current_medications", e.target.value)}
            placeholder="Warfarin, Digoxin, Amiodarone"
          />
        </div>

        <Button type="submit" icon={Send} loading={loading} disabled={!isValid} className="w-full">
          Run SepsisGuard pipeline
        </Button>
      </form>
    </Card>
  );
}
