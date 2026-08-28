// Top-level app shell — sets up routing between the SepsisGuard and CrossCare pages.

import { HashRouter, Routes, Route, Link } from "react-router-dom";
import SepsisGuard from "./pages/SepsisGuard.jsx";
import CrossCare from "./pages/CrossCare.jsx";

export default function App() {
  return (
    <HashRouter>
      <div className="min-h-screen bg-slate-950 text-slate-100">
        <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <span className="text-xl font-bold">MediGuard</span>
          <nav className="flex gap-4 text-sm">
            <Link to="/">SepsisGuard</Link>
            <Link to="/crosscare">CrossCare</Link>
          </nav>
        </header>
        <Routes>
          <Route path="/" element={<SepsisGuard />} />
          <Route path="/crosscare" element={<CrossCare />} />
        </Routes>
      </div>
    </HashRouter>
  );
}
