// Landing/overview page — hero, live stats, and entry points into both modules.

import {
  Activity, ArrowRight, Bed, BrainCircuit, ClipboardCheck, FileSignature,
  FlaskConical, Pill, ScanText, ShieldAlert, Sparkles, Stethoscope,
} from "lucide-react";
import { Link } from "react-router-dom";
import PageHeader from "../components/Layout/PageHeader.jsx";
import Badge, { severityTone } from "../components/ui/Badge.jsx";
import Card, { CardHeader } from "../components/ui/Card.jsx";
import { EmptyState } from "../components/ui/Spinner.jsx";
import { useSocket } from "../hooks/useMediGuardSocket.jsx";

const SEPSISGUARD_AGENTS = [
  { name: "Vitals Sentinel", icon: Activity },
  { name: "Clinical Strategist", icon: BrainCircuit },
  { name: "Pharmaco-Genomic", icon: FlaskConical },
  { name: "ICU Resource Broker", icon: Bed },
  { name: "Safety Auditor", icon: ClipboardCheck },
];

const CROSSCARE_AGENTS = [
  { name: "Prescription Ingestion", icon: ScanText },
  { name: "Pharmacology Interaction", icon: Pill },
  { name: "Physician Recommendation", icon: FileSignature },
];

export default function Overview() {
  const { status, lastSepsisAlert, lastInteractionResult } = useSocket();

  return (
    <div className="pb-16">
      <PageHeader
        eyebrow="MediGuard · API Cloud AI Hackathon 2026"
        title="Complete Patient Safety Platform"
        subtitle="8 autonomous AI agents watching for sepsis and dangerous drug interactions in real time — detecting, deciding, and documenting faster than a manual review ever could."
      />

      <div className="space-y-8 px-8 pt-8">
        {/* Hero */}
        <Card glow className="relative overflow-hidden">
          <div className="flex flex-col items-start gap-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="max-w-xl">
              <Badge tone="brand" icon={Sparkles}>Live multi-agent pipeline</Badge>
              <p className="mt-3 text-lg font-semibold text-base-50">
                Two modules, one mission: catch what a busy shift might miss.
              </p>
              <p className="mt-2 text-sm leading-relaxed text-base-400">
                <span className="text-base-200">SepsisGuard</span> detects early sepsis and dispatches a
                complete, safety-audited treatment plan in under 15 minutes.{" "}
                <span className="text-base-200">CrossCare</span> reads prescriptions across multiple
                doctors and flags dangerous drug combinations before they reach the patient.
              </p>
              <div className="mt-5 flex flex-wrap gap-3">
                <Link to="/sepsisguard" className="btn-primary">
                  <Stethoscope className="h-4 w-4" /> Open SepsisGuard <ArrowRight className="h-4 w-4" />
                </Link>
                <Link to="/crosscare" className="btn-secondary">
                  <Pill className="h-4 w-4" /> Open CrossCare <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
            <div className="flex shrink-0 flex-col gap-3 rounded-2xl border border-base-800 bg-base-850/60 p-4">
              <StatRow label="AI Agents" value="8" />
              <StatRow label="Modules" value="2" />
              <StatRow
                label="Live feed"
                value={status === "connected" ? "Online" : "Offline"}
                tone={status === "connected" ? "success" : "danger"}
              />
            </div>
          </div>
        </Card>

        {/* Pipeline overview */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader
              icon={Activity}
              title="SepsisGuard pipeline"
              subtitle="5 agents · vitals → treatment plan → signed audit"
            />
            <AgentChain agents={SEPSISGUARD_AGENTS} tone="brand" />
          </Card>
          <Card>
            <CardHeader
              icon={Pill}
              title="CrossCare pipeline"
              subtitle="3 agents · prescriptions → interactions → signed report"
            />
            <AgentChain agents={CROSSCARE_AGENTS} tone="accent" />
          </Card>
        </div>

        {/* Live activity */}
        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader icon={ShieldAlert} title="Latest sepsis alert" subtitle="Broadcast over the live WebSocket feed" />
            {lastSepsisAlert ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-base-100">{lastSepsisAlert.patient_id}</span>
                  <Badge tone={severityTone(lastSepsisAlert.severity)}>{lastSepsisAlert.severity}</Badge>
                </div>
                <p className="text-base-400">qSOFA score: {lastSepsisAlert.qsofa_score}</p>
                <p className="line-clamp-3 text-xs text-base-500">{lastSepsisAlert.sepsis_alert?.rationale}</p>
              </div>
            ) : (
              <EmptyState icon={ShieldAlert} title="No alerts yet" subtitle="Submit vitals in SepsisGuard to see live results here." />
            )}
          </Card>
          <Card>
            <CardHeader icon={Pill} title="Latest interaction check" subtitle="Broadcast over the live WebSocket feed" />
            {lastInteractionResult ? (
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-base-100">{lastInteractionResult.patient_id}</span>
                  <Badge tone={severityTone(lastInteractionResult.risk_level)}>{lastInteractionResult.risk_level} risk</Badge>
                </div>
                <p className="text-base-400">
                  {lastInteractionResult.dangerous_combinations?.length ?? 0} dangerous combination(s) found
                </p>
              </div>
            ) : (
              <EmptyState icon={Pill} title="No checks yet" subtitle="Submit a prescription in CrossCare to see live results here." />
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatRow({ label, value, tone = "neutral" }) {
  const toneClass = { neutral: "text-base-100", success: "text-emerald-400", danger: "text-red-400" }[tone];
  return (
    <div className="flex items-center justify-between gap-6 text-sm">
      <span className="text-base-400">{label}</span>
      <span className={`font-bold ${toneClass}`}>{value}</span>
    </div>
  );
}

function AgentChain({ agents, tone }) {
  const dotClass = tone === "brand" ? "bg-brand-500" : "bg-accent-500";
  return (
    <ol className="space-y-1">
      {agents.map(({ name, icon: Icon }, i) => (
        <li key={name} className="flex items-center gap-3 rounded-lg px-2 py-2 hover:bg-base-800/40">
          <span className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${dotClass}/15 text-[11px] font-bold text-base-100`}>
            {i + 1}
          </span>
          <Icon className="h-4 w-4 text-base-400" />
          <span className="text-sm text-base-200">{name}</span>
        </li>
      ))}
    </ol>
  );
}
