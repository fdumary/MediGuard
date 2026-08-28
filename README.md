# MediGuard

**Complete Patient Safety Platform**

MediGuard is an autonomous multi-agent AI system that protects hospital patients from two of the biggest killers in modern medicine — **sepsis** and **dangerous drug combinations**. It uses **8 specialized AI agents** powered by **LangGraph** and **Groq LLaMA 3.1** that work together autonomously to detect problems, recommend solutions, and alert the medical team in real time.

Built for the **API Cloud AI Hackathon 2026**.

---

## What is MediGuard?

MediGuard is a two-module patient-safety platform that sits between raw clinical data (vitals monitors, prescriptions) and the medical team, using autonomous AI agents to catch life-threatening problems faster than manual review ever could.

- **SepsisGuard** — continuously watches ICU vitals, detects early sepsis, and dispatches a complete treatment plan in under 15 minutes.
- **CrossCare** — reads prescriptions from multiple doctors and catches dangerous drug interactions before they reach the patient.

Both modules run on independent LangGraph workflows, share a common FastAPI backend, and stream live results to a React dashboard over WebSocket.

## The Problem

- **Sepsis** kills more hospital patients than any other single condition, and mortality rises roughly 8% for every hour treatment is delayed. Diagnosis relies on a nurse or doctor noticing a pattern across many vitals — something that is easy to miss during a busy shift.
- **Dangerous drug combinations** are common when a patient sees multiple specialists who don't see each other's prescriptions. No single doctor has the full picture, and manual cross-checking against every other active medication is impractical at scale.

Both problems share the same root cause: **critical signals are scattered across systems and people, and no one is watching all of it, all the time.**

## The Solution

MediGuard assigns each piece of this problem to a dedicated AI agent instead of one monolithic model. Specialized agents are easier to reason about, easier to audit, and can run in parallel — which is what makes a **sub-15-minute** sepsis response and **real-time** prescription screening possible.

- **SepsisGuard**: Detects early sepsis warning signs in ICU patients and automatically dispatches a complete treatment plan — antibiotics, bed allocation, and drug safety checks — in under 15 minutes.
- **CrossCare**: Reads patient prescriptions from multiple doctors, automatically detects dangerous drug combinations, and recommends safe alternatives using the NLM and RxNorm APIs.

## Architecture

```
                              ┌────────────────────────────┐
                              │        React Dashboard      │
                              │  (SepsisGuard / CrossCare)  │
                              └───────────────▲──────────────┘
                                              │ WebSocket + REST
                              ┌───────────────┴──────────────┐
                              │        FastAPI Backend        │
                              │   /api routes + /ws socket    │
                              └───────────────┬──────────────┘
                                              │
                 ┌────────────────────────────┴────────────────────────────┐
                 │                                                          │
     ┌───────────▼────────────┐                              ┌────────────▼────────────┐
     │   SepsisGuard Workflow   │                              │   CrossCare Workflow     │
     │        (LangGraph)       │                              │        (LangGraph)       │
     └───────────┬────────────┘                              └────────────┬────────────┘
                 │                                                          │
   1. Vitals Sentinel Agent                                   6. Prescription Ingestion Agent
      (reads vitals every 30s, qSOFA score)                       (OCR → FHIR MedicationStatement)
                 │ sepsis alert?                                            │
                 ▼                                                          ▼
   2. Clinical Strategist Agent                                7. Pharmacology Interaction Agent
      (orchestrates the response)                                  (RxNorm cross-check, risk level)
                 │                                                          │
        ┌────────┴────────┐                                                ▼
        ▼                 ▼                                    8. Physician Recommendation Agent
3. Pharmaco-Genomic   4. ICU Resource Broker                       (safe alternatives, clinical note)
   Agent (NLM API,       Agent (bed + pump,
   antibiotic + dose)     nurse notification)
        └────────┬────────┘
                 ▼
   5. Safety Auditor Agent
      (Surviving Sepsis Campaign
       compliance, approval, audit log)
                 │
                 ▼
          Treatment Plan → Dashboard + WebSocket broadcast
```

Both LangGraph workflows are compiled independently (`sepsisguard_workflow.py`, `crosscare_workflow.py`) and share the same underlying LLM client configuration (Groq LLaMA 3.1) and FastAPI process, but have no runtime dependency on each other.

## The 8 AI Agents

### SepsisGuard Agents

1. **Vitals Sentinel Agent** — Reads patient vitals every 30 seconds, calculates the qSOFA score, and triggers a sepsis alert when thresholds are crossed.
2. **Clinical Strategist Agent** — Orchestrates the entire emergency response, delegating tasks to the other agents and assembling the final treatment plan.
3. **Pharmaco-Genomic Agent** — Checks the NLM API for drug interactions, recommends the correct antibiotics, and calculates a safe dosage.
4. **ICU Resource Broker Agent** — Checks ICU bed availability, reserves an infusion pump, and notifies nursing staff.
5. **Safety Auditor Agent** — Verifies compliance with Surviving Sepsis Campaign rules, gives final approval before treatment, and creates the audit log.

### CrossCare Agents

6. **Prescription Ingestion Agent** — Reads prescriptions via OCR, extracts medicine names and dosages, and converts them into FHIR format.
7. **Pharmacology Interaction Agent** — Cross-checks all drugs via the RxNorm API, detects dangerous combinations, and flags kidney and heart risks.
8. **Physician Recommendation Agent** — Suggests safe alternative medicines, writes a clinical note for the doctor, and sends an alert with recommendations.

## Tech Stack

| Layer              | Technology                              |
|---------------------|------------------------------------------|
| Agent Framework     | LangGraph                                |
| LLM                 | Groq LLaMA 3.1 8B Instant (free)         |
| Medical APIs        | NLM API + RxNorm API (free)              |
| Backend             | FastAPI (Python)                         |
| Frontend            | React + Tailwind CSS                     |
| Real-time           | WebSocket                                |
| Database            | SQLite (hackathon build)                 |
| Deployment          | Render (free tier)                       |
| Patient Data        | Simulated FHIR JSON                      |

## Project Structure

```
mediguard/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── vitals_sentinel_agent.py
│   │   ├── clinical_strategist_agent.py
│   │   ├── pharmaco_genomic_agent.py
│   │   ├── icu_resource_broker_agent.py
│   │   ├── safety_auditor_agent.py
│   │   ├── prescription_ingestion_agent.py
│   │   ├── pharmacology_interaction_agent.py
│   │   └── physician_recommendation_agent.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── sepsisguard_workflow.py
│   │   ├── crosscare_workflow.py
│   │   └── state.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── vitals_prompt.py
│   │   ├── strategist_prompt.py
│   │   ├── pharmaco_prompt.py
│   │   ├── resource_prompt.py
│   │   ├── auditor_prompt.py
│   │   ├── ingestion_prompt.py
│   │   ├── interaction_prompt.py
│   │   └── recommendation_prompt.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── nlm_api_tool.py
│   │   ├── rxnorm_api_tool.py
│   │   ├── sofa_calculator.py
│   │   └── fhir_parser.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── data/
│   │   ├── simulated_patients.json
│   │   └── drug_database.json
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── main.py
│   ├── requirements.txt
│   ├── Procfile
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── PatientCard.jsx
│   │   │   ├── AgentPipeline.jsx
│   │   │   ├── AlertPanel.jsx
│   │   │   ├── DrugInteractionPanel.jsx
│   │   │   └── VitalsChart.jsx
│   │   ├── pages/
│   │   │   ├── SepsisGuard.jsx
│   │   │   └── CrossCare.jsx
│   │   ├── lib/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env
├── .gitignore
└── README.md
```

## How to Run

### Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your GROQ_API_KEY and NLM_API_KEY

uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The dashboard will be available at `http://localhost:5173` (default Vite port) and will connect to the backend at the URL configured in `frontend/.env`.

## API Endpoints

| Method | Endpoint                        | Description                                                        |
|--------|----------------------------------|----------------------------------------------------------------------|
| GET    | `/`                              | Health message confirming the API is running.                      |
| GET    | `/api/health`                    | Simple health check for uptime monitoring.                         |
| GET    | `/api/patients`                  | Returns the list of simulated ICU patients.                        |
| POST   | `/api/sepsisguard/vitals`        | Submits a vitals reading and runs the SepsisGuard LangGraph pipeline. |
| POST   | `/api/crosscare/prescriptions`   | Submits a prescription and runs the CrossCare LangGraph pipeline.  |
| WS     | `/ws`                            | Live WebSocket feed broadcasting sepsis alerts and drug interaction results. |

## Environment Variables

Backend (`backend/.env`, based on `backend/.env.example`):

```
GROQ_API_KEY=your_groq_key_here
NLM_API_KEY=your_nlm_key_here
```

Frontend (`frontend/.env`):

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

## Team

_team portion._

## Hackathon

Built for the **API Cloud AI Hackathon 2026** — Devpost, **September 2–3, 2026**.
