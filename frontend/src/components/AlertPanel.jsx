// Shows the live sepsis alert feed pushed over the WebSocket connection.

export default function AlertPanel({ alerts }) {
  return (
    <div className="space-y-2">
      {alerts.length === 0 && <p className="text-sm text-slate-500">No active alerts.</p>}
      {alerts.map((alert, idx) => (
        <div key={idx} className="rounded-lg border border-red-900 bg-red-950/40 p-3">
          <div className="flex justify-between text-sm font-semibold text-red-300">
            <span>{alert.patient_id}</span>
            <span>qSOFA {alert.qsofa_score}</span>
          </div>
          <p className="text-xs text-red-400 uppercase">{alert.severity}</p>
          <p className="mt-1 text-xs text-slate-300">{alert.rationale}</p>
        </div>
      ))}
    </div>
  );
}
