// Fetch/WebSocket client wrapping the MediGuard FastAPI backend. Covers
// every endpoint in backend/api/routes.py.

export function getApiBaseUrl() {
  const custom = import.meta.env.VITE_API_BASE_URL;
  if (custom !== undefined && custom !== "") {
    return custom.replace(/\/+$/, "");
  }
  if (typeof window !== "undefined") {
    // If running in local dev on localhost
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return "http://localhost:8000";
    }
    // In production on Vercel or cloud deployments, make same-origin requests
    return "";
  }
  return "http://localhost:8000";
}

export function getWsUrls() {
  const custom = import.meta.env.VITE_WS_URL;
  if (custom !== undefined && custom !== "") {
    return [custom];
  }
  if (typeof window !== "undefined") {
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
      return ["ws://localhost:8000/ws", "ws://localhost:8000/api/ws"];
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    return [`${protocol}//${host}/ws`, `${protocol}//${host}/api/ws`];
  }
  return ["ws://localhost:8000/ws", "ws://localhost:8000/api/ws"];
}

const API_BASE_URL = getApiBaseUrl();

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
  const urls = getWsUrls();
  let currentIdx = 0;
  let socket = null;
  let pingInterval = null;
  let isClosed = false;

  function tryConnect() {
    if (isClosed) return;
    const url = urls[currentIdx];
    try {
      socket = new WebSocket(url);
    } catch (e) {
      onStatusChange?.("error");
      return;
    }

    socket.onopen = () => {
      onStatusChange?.("connected");
      // Keep-alive heartbeat: send ping every 15s to keep connection open on Vercel / serverless
      if (pingInterval) clearInterval(pingInterval);
      pingInterval = setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
          try {
            socket.send("ping");
          } catch {
            // ignore send error
          }
        }
      }, 15000);
    };

    socket.onclose = () => {
      if (pingInterval) clearInterval(pingInterval);
      if (!isClosed) {
        // Rotate to alternate URL for next retry
        currentIdx = (currentIdx + 1) % urls.length;
        onStatusChange?.("disconnected");
      }
    };

    socket.onerror = () => {
      onStatusChange?.("error");
    };

    socket.onmessage = (event) => {
      try {
        if (event.data === "pong") return;
        const data = JSON.parse(event.data);
        if (data.type === "pong" || data.type === "connection_established") {
          onStatusChange?.("connected");
          return;
        }
        onMessage(data);
      } catch {
        // ignore non-JSON frames
      }
    };
  }

  tryConnect();

  return {
    close() {
      isClosed = true;
      if (pingInterval) clearInterval(pingInterval);
      if (socket) socket.close();
    },
    send(data) {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(typeof data === "string" ? data : JSON.stringify(data));
      }
    },
    get raw() {
      return socket;
    },
  };
}
