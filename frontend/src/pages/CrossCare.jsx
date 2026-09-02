// CrossCare page — prescription input (manual or PDF), live agent pipeline, and full results.

import { FileSignature, Pill, ScanText } from "lucide-react";
import { useState } from "react";
import PageHeader from "../components/Layout/PageHeader.jsx";
import PipelineTracker from "../components/PipelineTracker.jsx";
import PrescriptionPanel from "../components/CrossCare/PrescriptionPanel.jsx";
import ResultsPanel from "../components/CrossCare/ResultsPanel.jsx";
import Card, { CardHeader } from "../components/ui/Card.jsx";
import { useToast } from "../components/ui/Toast.jsx";
import { submitPrescription, uploadPrescriptionPdf } from "../lib/api.js";

const STEPS = [
  { name: "Prescription Ingestion", icon: ScanText, didRun: (r) => (r.medicines ?? []).length > 0 },
  { name: "Pharmacology Interaction", icon: Pill, didRun: (r) => r.risk_level !== undefined },
  { name: "Physician Recommendation", icon: FileSignature, didRun: (r) => (r.recommendations ?? []).length >= 0 && r.clinical_note !== undefined },
];

export default function CrossCare() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const { pushToast } = useToast();

  async function runPipeline(promise) {
    setLoading(true);
    setResult(null);
    try {
      const data = await promise;
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
        eyebrow="Module 2"
        title="CrossCare"
        subtitle="Reads prescriptions from multiple doctors, detects dangerous drug combinations, and recommends safe alternatives."
      />

      <div className="grid gap-6 px-8 pt-8 lg:grid-cols-[380px_1fr]">
        <div className="space-y-6">
          <PrescriptionPanel
            onSubmitManual={(prescription) => runPipeline(submitPrescription(prescription))}
            onSubmitPdf={(payload) => runPipeline(uploadPrescriptionPdf(payload))}
            loading={loading}
          />
          <Card>
            <CardHeader title="Agent pipeline" subtitle="3 CrossCare agents" />
            <PipelineTracker steps={STEPS} isRunning={loading} result={result} />
          </Card>
        </div>

        <ResultsPanel result={result} />
      </div>
    </div>
  );
}
