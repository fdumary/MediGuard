// Displays the full CrossCare pipeline result: dangerous combinations,
// risk level, recommendations, medication timeline, and a signed PDF download.

import {
  AlertOctagon, CalendarClock, CheckCircle2, Download, Droplet,
  HeartPulse, MessageSquareWarning, Pill,
} from "lucide-react";
import Badge, { severityTone } from "../ui/Badge.jsx";
import Card, { CardHeader } from "../ui/Card.jsx";
import { EmptyState } from "../ui/Spinner.jsx";
import TypewriterText from "../ui/TypewriterText.jsx";
import { downloadReportUrl } from "../../lib/api.js";

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <Card className="h-full">
        <EmptyState
          icon={Pill}
          title="No pipeline run yet"
          subtitle="Submit a prescription to see detected interactions, recommendations, and the signed report here."
        />
      </Card>
    );
  }

  const combos = result.dangerous_combinations ?? [];
  const medicationPlan = result.medication_plan ?? [];
  const displayName = result.patient_name || result.patient_id;

  return (
    <div className="space-y-6">
      <Card glow={combos.length > 0}>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-base-50">{displayName}</span>
          <span className="text-xs text-base-500">({result.patient_id})</span>
        </div>
        <div className="flex items-center justify-between gap-3">
          <Badge tone={severityTone(result.risk_level)} icon={combos.length > 0 ? AlertOctagon : CheckCircle2}>
            {result.risk_level ?? "unknown"} risk
          </Badge>
          <div className="flex gap-2">
            {"kidney_risk" in result && (
              <Badge tone={result.kidney_risk ? "danger" : "success"} icon={Droplet}>
                Kidney {result.kidney_risk ? "risk" : "clear"}
              </Badge>
            )}
            {"heart_risk" in result && (
              <Badge tone={result.heart_risk ? "danger" : "success"} icon={HeartPulse}>
                Heart {result.heart_risk ? "risk" : "clear"}
              </Badge>
            )}
          </div>
        </div>

        {combos.length > 0 ? (
          <ul className="mt-4 space-y-1.5">
            {combos.map((c, i) => (
              <li
                key={i}
                className="flex animate-fade-in items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-2 text-sm text-red-300"
                style={{ animationDelay: `${i * 90}ms`, animationFillMode: "backwards" }}
              >
                <AlertOctagon className="h-4 w-4 shrink-0" />
                {c}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-sm text-emerald-400">No dangerous combinations detected.</p>
        )}
      </Card>

      {result.recommendations?.length > 0 && (
        <Card>
          <CardHeader title="Recommendations" subtitle="A concrete next step for every flagged risk" />
          <ul className="space-y-2">
            {result.recommendations.map((rec, i) => (
              <li
                key={i}
                className="animate-fade-in text-sm leading-relaxed text-base-300"
                style={{ animationDelay: `${i * 90}ms`, animationFillMode: "backwards" }}
              >
                <span className="mr-2 text-brand-400">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {medicationPlan.length > 0 && (
        <Card>
          <CardHeader icon={CalendarClock} title="Recommended medication plan" subtitle="Final plan and timeline for this patient" />
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-base-800 text-xs uppercase tracking-wide text-base-500">
                  <th className="py-2 pr-3 font-medium">Medication</th>
                  <th className="py-2 pr-3 font-medium">Dosage</th>
                  <th className="py-2 pr-3 font-medium">Timing</th>
                </tr>
              </thead>
              <tbody>
                {medicationPlan.map((item, i) => (
                  <tr key={i} className="border-b border-base-800/60 align-top">
                    <td className="py-2.5 pr-3 font-semibold text-base-100">{item.drug}</td>
                    <td className="py-2.5 pr-3 text-base-300">{item.dosage}</td>
                    <td className="py-2.5 pr-3 text-base-300">
                      {item.timing}
                      {item.notes && <p className="mt-0.5 text-xs text-base-500">{item.notes}</p>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {result.clinical_note && (
        <Card>
          <CardHeader icon={MessageSquareWarning} title="Clinical note" />
          <TypewriterText text={result.clinical_note} className="text-sm leading-relaxed text-base-300" />
        </Card>
      )}

      {result.alert_message && (
        <Card>
          <CardHeader title="Physician alert" />
          <TypewriterText
            text={result.alert_message}
            className="rounded-lg bg-base-850/60 p-3 text-sm leading-relaxed text-base-300"
          />
        </Card>
      )}

      {result.drug_report_pdf_base64 && (
        <a
          href={downloadReportUrl(result.patient_id)}
          className="btn-secondary w-full"
          download={`drug_report_${displayName}.pdf`}
        >
          <Download className="h-4 w-4" /> Download drug interaction report PDF
        </a>
      )}
    </div>
  );
}
