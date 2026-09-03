// Connects to the MediGuard WebSocket once at the app root and fans out
// live events (sepsis alerts, drug interaction results) to any page via
// context, while also surfacing them as toast notifications.
// Includes automatic HTTP polling fallback for serverless platforms (Vercel).

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { connectMediGuardSocket, getLatestFeed } from "../lib/api";
import { useToast } from "../components/ui/Toast";

const SocketContext = createContext(null);

export function SocketProvider({ children }) {
  const [status, setStatus] = useState("connecting");
  const [lastSepsisAlert, setLastSepsisAlert] = useState(null);
  const [lastInteractionResult, setLastInteractionResult] = useState(null);
  const { pushToast } = useToast();
  const socketConnectedRef = useRef(false);

  useEffect(() => {
    let disposed = false;
    let socket;
    let retryTimer;

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

    const pollFallback = async () => {
      if (disposed) return;
      try {
        const feed = await getLatestFeed();
        if (feed && feed.status === "online") {
          if (!socketConnectedRef.current) {
            setStatus("connected");
          }
          if (feed.latest_sepsis_alert) {
            setLastSepsisAlert(feed.latest_sepsis_alert);
          }
          if (feed.latest_interaction_result) {
            setLastInteractionResult(feed.latest_interaction_result);
          }
        }
      } catch {
        if (!socketConnectedRef.current) {
          setStatus("disconnected");
        }
      }
    };

    const connect = () => {
      if (disposed) return;
      socket = connectMediGuardSocket(handleMessage, (s) => {
        if (disposed) return;
        if (s === "connected") {
          socketConnectedRef.current = true;
          setStatus("connected");
        } else {
          socketConnectedRef.current = false;
          // If socket drops, immediately poll HTTP fallback to check if backend is alive
          pollFallback();
          if (s === "disconnected") {
            clearTimeout(retryTimer);
            retryTimer = setTimeout(connect, 3000);
          }
        }
      });
    };

    connect();
    pollFallback();

    // Heartbeat poll every 6s to ensure the feed never stays offline if socket drops
    const pollTimer = setInterval(() => {
      if (!socketConnectedRef.current) {
        pollFallback();
      }
    }, 6000);

    return () => {
      disposed = true;
      socketConnectedRef.current = false;
      clearTimeout(retryTimer);
      clearInterval(pollTimer);
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
