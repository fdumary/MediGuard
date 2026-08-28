// Thin fetch/WebSocket client wrapping the MediGuard FastAPI backend.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";

export async function getPatients() {
  const res = await fetch(`${API_BASE_URL}/api/patients`);
  return res.json();
}

export async function submitVitals(vitals) {
  const res = await fetch(`${API_BASE_URL}/api/sepsisguard/vitals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(vitals),
  });
  return res.json();
}

export async function submitPrescription(prescription) {
  const res = await fetch(`${API_BASE_URL}/api/crosscare/prescriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(prescription),
  });
  return res.json();
}

export function connectMediGuardSocket(onMessage) {
  const socket = new WebSocket(WS_URL);
  socket.onmessage = (event) => onMessage(JSON.parse(event.data));
  return socket;
}
