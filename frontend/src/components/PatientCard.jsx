// Displays a single patient's identity and latest vitals in a compact card.

export default function PatientCard({ patient }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{patient.name}</h3>
        <span className="text-xs text-slate-400">{patient.patient_id}</span>
      </div>
      <p className="text-sm text-slate-400">Age {patient.age}</p>
      <div className="mt-2 grid grid-cols-2 gap-1 text-xs text-slate-300">
        <span>HR: {patient.heart_rate} bpm</span>
        <span>BP: {patient.blood_pressure}</span>
        <span>Temp: {patient.temperature} °C</span>
        <span>RR: {patient.respiratory_rate}/min</span>
        <span>Lactate: {patient.lactate} mmol/L</span>
        <span>WBC: {patient.wbc_count} k/uL</span>
      </div>
    </div>
  );
}
