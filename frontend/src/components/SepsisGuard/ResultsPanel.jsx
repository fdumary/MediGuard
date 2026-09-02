// Displays the full SepsisGuard pipeline result: alert, treatment plan,
// ICU resources, and the safety audit outcome with a signed PDF download.

import {
  Bed, CheckCircle2, Download, FileWarning,
  ShieldCheck, ShieldX, Syringe, XCircle,
} from "lucide-react";
import Badge, { severityTone } from "../ui/Badge.jsx";
import Card, { CardHeader } from "../ui/Card.jsx";
import { EmptyState } from "../ui/Spinner.jsx";
import TypewriterText from "../ui/TypewriterText.jsx";
import { downloadAuditUrl } from "../../lib/api.js";

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <Card className="h-full">
        <EmptyState
          icon={ShieldCheck}
          title="No pipeline run yet"
          subtitle="Submit vitals to see the sepsis alert, treatment plan, and signed audit report here."
        />
      </Card>
    );
  }

  if (!result.sepsis_alert) {
    return (
      <Card className="h-full">
        <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
          <CheckCircle2 className="h-10 w-10 text-emerald-400" />
          <p className="text-sm font-semibold text-base-100">No sepsis detected</p>
          <p className="max-w-xs text-xs text-base-500">
            qSOFA score {result.qsofa_score} did not cross the alert threshold (≥2). The pipeline stopped
            after the Vitals Sentinel agent — no treatment plan was generated.
          </p>
        </div>
      </Card>
    );
  }

  const displayName = result.patient_name || result.patient_id;

  return (
    <div className="space-y-6">
      <Card glow>
        <div className="flex items-start justify-between gap-3">
          <div className="w-full">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="text-sm font-semibold text-base-50">{displayName}</span>
              <span className="text-xs text-base-500">({result.patient_id})</span>
              <Badge tone={severityTone(result.severity)}>{result.severity} sepsis</Badge>
              <Badge tone="neutral">qSOFA {result.qsofa_score}/3</Badge>
            </div>
            <TypewriterText
              text={result.sepsis_alert?.rationale}
              className="text-sm leading-relaxed text-base-300"
            />
          </div>
        </div>
        {result.suspected_infection_source && (
          <p className="mt-3 text-xs text-base-500">
            Suspected source: <span className="text-base-300">{result.suspected_infection_source}</span>
          </p>
        )}
      </Card>

      {result.priority_actions?.length > 0 && (
        <Card>
          <CardHeader title="Priority actions (1-hour bundle)" />
          <ul className="space-y-1.5">
            {result.priority_actions.map((action, i) => (
              <li
                key={i}
                className="flex animate-fade-in gap-2.5 text-sm text-base-300"
                style={{ animationDelay: `${i * 90}ms`, animationFillMode: "backwards" }}
              >
                <span className="mt-0.5 text-brand-400">•</span>
                {action}
              </li>
            ))}
          </ul>
        </Card>
      )}

      <Card>
        <CardHeader icon={Syringe} title="Treatment plan" />
        <div className="grid gap-2 sm:grid-cols-2">
          {(result.antibiotics ?? []).map((abx, i) => (
            <div key={i} className="rounded-lg border border-base-800 bg-base-850/60 p-3">
              <p className="text-sm font-semibold text-base-100">{abx}</p>
              <p className="text-xs text-base-500">{result.dosages?.[i]}</p>
            </div>
          ))}
        </div>
        {result.contraindication_warnings?.length > 0 && (
          <div className="mt-3 space-y-1.5 rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
            <p className="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
              <FileWarning className="h-3.5 w-3.5" /> Contraindication warnings
            </p>
            {result.contraindication_warnings.map((w, i) => (
              <p
                key={i}
                className="animate-fade-in text-xs text-base-400"
                style={{ animationDelay: `${i * 90}ms`, animationFillMode: "backwards" }}
              >
                {w}
              </p>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <CardHeader icon={Bed} title="ICU resources" />
        <div className="flex flex-wrap gap-3 text-sm">
          <Badge tone={result.icu_bed_reserved ? "success" : "danger"}>
            Bed {result.bed_id ?? "—"}
          </Badge>
          <Badge tone={result.infusion_pump_reserved ? "success" : "danger"}>
            Pump {result.pump_id ?? "—"}
          </Badge>
        </div>
        {result.nursing_message && (
          <TypewriterText
            text={result.nursing_message}
            className="mt-3 text-xs leading-relaxed text-base-400"
          />
        )}
      </Card>

      <Card>
        <CardHeader
          icon={result.approved ? ShieldCheck : ShieldX}
          title="Safety Auditor decision"
          action={
            <Badge tone={result.approved ? "success" : "danger"} icon={result.approved ? CheckCircle2 : XCircle}>
              {result.approved ? "Approved" : "Rejected"}
            </Badge>
          }
        />
        {result.compliance_violations?.length > 0 && (
          <ul className="mb-3 space-y-1.5">
            {result.compliance_violations.map((v, i) => (
              <li
                key={i}
                className="flex animate-fade-in gap-2 text-xs text-red-300"
                style={{ animationDelay: `${i * 90}ms`, animationFillMode: "backwards" }}
              >
                <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                {v}
              </li>
            ))}
          </ul>
        )}
        <p className="rounded-lg bg-base-850/60 p-2.5 font-mono text-[11px] leading-relaxed text-base-500">
          {result.audit_log}
        </p>

        {result.signed_audit_pdf_base64 ? (
          <a
            href={downloadAuditUrl(result.patient_id)}
            className="btn-secondary mt-4 w-full"
            download={`audit_${displayName}.pdf`}
          >
            <Download className="h-4 w-4" /> Download signed audit PDF
          </a>
        ) : (
          result.nutrient_warning && (
            <p className="mt-4 flex items-center gap-1.5 text-xs text-amber-400">
              <FileWarning className="h-3.5 w-3.5" /> {result.nutrient_warning}
            </p>
          )
        )}
      </Card>
    </div>
  );
}
