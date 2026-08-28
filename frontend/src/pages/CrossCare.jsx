// CrossCare dashboard page — submit prescriptions and view live drug interaction results.

import { useEffect, useState } from "react";
import Dashboard from "../components/Dashboard.jsx";
import AgentPipeline from "../components/AgentPipeline.jsx";
import DrugInteractionPanel from "../components/DrugInteractionPanel.jsx";
import { connectMediGuardSocket, submitPrescription } from "../lib/api.js";

const CROSSCARE_AGENTS = [
  "Prescription Ingestion",
  "Pharmacology Interaction",
  "Physician Recommendation",
];

export default function CrossCare() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    const socket = connectMediGuardSocket((message) => {
      if (message.type === "drug_interaction_result") {
        setResult(message.data);
      }
    });
    return () => socket.close();
  }, []);

  const handleDemoSubmit = async () => {
    const response = await submitPrescription({
      patient_id: "P-003",
      doctor_name: "Dr. Patel",
      medicines: ["Warfarin", "Amiodarone"],
      dosages: ["5mg daily", "200mg daily"],
      conditions: ["Atrial fibrillation"],
    });
    setResult(response);
  };

  return (
    <Dashboard title="CrossCare">
      <div className="space-y-4">
        <button
          onClick={handleDemoSubmit}
          className="rounded bg-sky-600 hover:bg-sky-500 px-4 py-2 text-sm font-medium"
        >
          Submit Demo Prescription
        </button>
        <AgentPipeline agents={CROSSCARE_AGENTS.map((name) => ({ name, status: "idle" }))} />
      </div>
      <DrugInteractionPanel result={result} />
    </Dashboard>
  );
}
