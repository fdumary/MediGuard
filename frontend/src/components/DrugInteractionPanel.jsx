// Displays CrossCare's detected dangerous drug combinations and recommendations.

export default function DrugInteractionPanel({ result }) {
  if (!result) return <p className="text-sm text-slate-500">No prescription analyzed yet.</p>;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4 space-y-3">
      <div className="flex justify-between">
        <span className="font-semibold">{result.patient_id}</span>
        <span className="text-xs uppercase text-amber-400">{result.risk_level} risk</span>
      </div>

      <div>
        <h4 className="text-xs font-semibold text-slate-400">Dangerous combinations</h4>
        <ul className="text-sm text-red-300 list-disc list-inside">
          {(result.dangerous_combinations || []).map((combo, idx) => (
            <li key={idx}>{combo}</li>
          ))}
        </ul>
      </div>

      <div>
        <h4 className="text-xs font-semibold text-slate-400">Recommendations</h4>
        <ul className="text-sm text-emerald-300 list-disc list-inside">
          {(result.recommendations || []).map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      </div>

      <p className="text-xs text-slate-400 whitespace-pre-wrap">{result.clinical_note}</p>
    </div>
  );
}
