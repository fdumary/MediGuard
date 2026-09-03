// Connects to the MediGuard WebSocket once at the app root and fans out
// live events (sepsis alerts, drug interaction results) to any page via
// context, while also surfacing them as toast notifications.

import { createContext, useContext, useEffect, useState } from "react";
import { connectMediGuardSocket } from "../lib/api";
import { useToast } from "../components/ui/Toast";

const SocketContext = createContext(null);

export function SocketProvider({ children }) {
  const [status, setStatus] = useState("connecting");
  const [lastSepsisAlert, setLastSepsisAlert] = useState(null);
  const [lastInteractionResult, setLastInteractionResult] = useState(null);
  const { pushToast } = useToast();

  useEffect(() => {
    let disposed = false;
    let socket;
    let retryTimer;
    let failureCount = 0;

    const handleMessage = (message) => {
      if (message.type === "sepsis_alert" && message.data?.sepsis_alert) {
        setLastSepsisAlert(message.data);
        pushToast({
          tone: "danger",
          title: `Sepsis alert — ${message.data.patient_id}`,
          description: `qSOFA ${message.data.qsofa_score} · ${message.data.severity} severity`,
        });
      }
      if (message.type === "drug_interaction_result") {
        setLastInteractionResult(message.data);
        const combos = message.data?.dangerous_combinations?.length ?? 0;
        if (combos > 0) {
          pushToast({
            tone: "info",
            title: `Drug interaction check — ${message.data.patient_id}`,
            description: `${combos} dangerous combination${combos === 1 ? "" : "s"} found (${message.data.risk_level} risk)`,
          });
        }
      }
    };

    const connect = () => {
      if (disposed) return;
      socket = connectMediGuardSocket(handleMessage, (s) => {
        if (disposed) return;
        if (s === "connected") {
          failureCount = 0;
          setStatus("connected");
        } else if (s === "disconnected" || s === "error") {
          failureCount++;
          // Give 2 transient retry attempts as 'connecting' before marking 'disconnected'
          if (failureCount < 3) {
            setStatus("connecting");
          } else {
            setStatus("disconnected");
          }
          if (s === "disconnected") {
            clearTimeout(retryTimer);
            retryTimer = setTimeout(connect, 2000);
          }
        }
      });
    };
    connect();

    return () => {
      disposed = true;
      clearTimeout(retryTimer);
      socket?.close();
    };
  }, [pushToast]);

  return (
    <SocketContext.Provider value={{ status, lastSepsisAlert, lastInteractionResult }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const ctx = useContext(SocketContext);
  if (!ctx) throw new Error("useSocket must be used within SocketProvider");
  return ctx;
}
