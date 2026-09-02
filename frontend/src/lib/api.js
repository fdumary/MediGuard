// Fetch/WebSocket client wrapping the MediGuard FastAPI backend. Covers
// every endpoint in backend/api/routes.py.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

async function handle(res) {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // response wasn't JSON — keep statusText
    }
    throw new Error(`${res.status} ${detail}`);
  }
  return res;
}

export async function getPatients() {
  const res = await fetch(`${API_BASE_URL}/api/patients`);
  return (await handle(res)).json();
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  return (await handle(res)).json();
}

export async function submitVitals(vitals) {
  const res = await fetch(`${API_BASE_URL}/api/sepsisguard/vitals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vitals),
  });
  return (await handle(res)).json();
}

export async function submitPrescription(prescription) {
  const res = await fetch(`${API_BASE_URL}/api/crosscare/prescriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prescription),
  });
  return (await handle(res)).json();
}

export async function uploadPrescriptionPdf({ patientId, patientName = "", doctorName = "", file }) {
  const form = new FormData();
  form.append("file", file);
  const params = new URLSearchParams({
    patient_id: patientId,
    patient_name: patientName,
    doctor_name: doctorName,
  });
  const res = await fetch(`${API_BASE_URL}/api/upload-prescription?${params.toString()}`, {
    method: "POST",
    body: form,
  });
  return (await handle(res)).json();
}

export function downloadAuditUrl(patientId) {
  return `${API_BASE_URL}/api/download-audit/${encodeURIComponent(patientId)}`;
}

export function downloadReportUrl(patientId) {
  return `${API_BASE_URL}/api/download-report/${encodeURIComponent(patientId)}`;
}

export function connectMediGuardSocket(onMessage, onStatusChange) {
  const socket = new WebSocket(WS_URL);
  socket.onopen = () => onStatusChange?.("connected");
  socket.onclose = () => onStatusChange?.("disconnected");
  socket.onerror = () => onStatusChange?.("error");
  socket.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data));
    } catch {
      // ignore non-JSON frames
    }
  };
  return socket;
}
