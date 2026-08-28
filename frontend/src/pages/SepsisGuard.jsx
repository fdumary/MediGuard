// SepsisGuard dashboard page — live ICU patient cards, agent pipeline status, and sepsis alerts.

import { useEffect, useState } from "react";
import Dashboard from "../components/Dashboard.jsx";
import PatientCard from "../components/PatientCard.jsx";
import AgentPipeline from "../components/AgentPipeline.jsx";
import AlertPanel from "../components/AlertPanel.jsx";
import { getPatients, connectMediGuardSocket } from "../lib/api.js";

const SEPSISGUARD_AGENTS = [
  "Vitals Sentinel",
  "Clinical Strategist",
  "Pharmaco-Genomic",
  "ICU Resource Broker",
  "Safety Auditor",
];

export default function SepsisGuard() {
  const [patients, setPatients] = useState([]);
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    getPatients().then(setPatients).catch(() => setPatients([]));

    const socket = connectMediGuardSocket((message) => {
      if (message.type === "sepsis_alert" && message.data?.sepsis_alert) {
        setAlerts((prev) => [message.data.sepsis_alert, ...prev]);
      }
    });
    return () => socket.close();
  }, []);

  return (
    <Dashboard title="SepsisGuard">
      <div className="space-y-4">
        <h2 className="text-sm font-semibold text-slate-400">ICU Patients</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {patients.map((p) => (
            <PatientCard key={p.patient_id} patient={p} />
          ))}
        </div>
        <AgentPipeline agents={SEPSISGUARD_AGENTS.map((name) => ({ name, status: "idle" }))} />
      </div>
      <div>
        <h2 className="text-sm font-semibold text-slate-400 mb-2">Live Sepsis Alerts</h2>
        <AlertPanel alerts={alerts} />
      </div>
    </Dashboard>
  );
}
