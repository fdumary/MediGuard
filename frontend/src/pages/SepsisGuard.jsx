// SepsisGuard page — vitals form, live agent pipeline, and full results.

import { Activity, Bed, BrainCircuit, ClipboardCheck, FlaskConical } from "lucide-react";
import { useState } from "react";
import PageHeader from "../components/Layout/PageHeader.jsx";
import PipelineTracker from "../components/PipelineTracker.jsx";
import ResultsPanel from "../components/SepsisGuard/ResultsPanel.jsx";
import VitalsPanel from "../components/SepsisGuard/VitalsPanel.jsx";
import Card, { CardHeader } from "../components/ui/Card.jsx";
import { useToast } from "../components/ui/Toast.jsx";
import { submitVitals } from "../lib/api.js";

const STEPS = [
  { name: "Vitals Sentinel", icon: Activity, didRun: (r) => r.qsofa_score !== undefined },
  { name: "Clinical Strategist", icon: BrainCircuit, didRun: (r) => !!r.strategy_summary },
  { name: "Pharmaco-Genomic", icon: FlaskConical, didRun: (r) => (r.antibiotics ?? []).length > 0 },
  { name: "ICU Resource Broker", icon: Bed, didRun: (r) => r.icu_bed_reserved !== undefined },
  { name: "Safety Auditor", icon: ClipboardCheck, didRun: (r) => r.approved !== undefined },
];

export default function SepsisGuard() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const { pushToast } = useToast();

  async function handleSubmit(vitals) {
    setLoading(true);
    setResult(null);
    try {
      const data = await submitVitals(vitals);
      setResult(data);
    } catch (err) {
      pushToast({ tone: "danger", title: "Pipeline failed", description: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="pb-16">
      <PageHeader
        eyebrow="Module 1"
        title="SepsisGuard"
        subtitle="Detects early sepsis warning signs and dispatches a complete, safety-audited treatment plan in under 15 minutes."
      />

      <div className="grid gap-6 px-8 pt-8 lg:grid-cols-[380px_1fr]">
        <div className="space-y-6">
          <VitalsPanel onSubmit={handleSubmit} loading={loading} />
          <Card>
            <CardHeader title="Agent pipeline" subtitle="5 SepsisGuard agents" />
            <PipelineTracker steps={STEPS} isRunning={loading} result={result} />
          </Card>
        </div>

        <ResultsPanel result={result} />
      </div>
    </div>
  );
}
