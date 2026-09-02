// Top-level app shell — sidebar navigation, toast/socket providers, and routing.

import { HashRouter, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Layout/Sidebar.jsx";
import { ToastProvider } from "./components/ui/Toast.jsx";
import { SocketProvider } from "./hooks/useMediGuardSocket.jsx";
import Overview from "./pages/Overview.jsx";
import SepsisGuard from "./pages/SepsisGuard.jsx";
import CrossCare from "./pages/CrossCare.jsx";

export default function App() {
  return (
    <ToastProvider>
      <SocketProvider>
        <HashRouter>
          <div className="min-h-screen bg-base-950">
            <div
              className="pointer-events-none fixed inset-0 z-0 opacity-40"
              style={{
                background:
                  "radial-gradient(circle at 15% 0%, rgba(45,212,191,0.08), transparent 40%), radial-gradient(circle at 85% 20%, rgba(59,130,246,0.08), transparent 40%)",
              }}
            />
            <Sidebar />
            <main className="relative z-10 ml-64 min-h-screen">
              <Routes>
                <Route path="/" element={<Overview />} />
                <Route path="/sepsisguard" element={<SepsisGuard />} />
                <Route path="/crosscare" element={<CrossCare />} />
              </Routes>
            </main>
          </div>
        </HashRouter>
      </SocketProvider>
    </ToastProvider>
  );
}
