// Visualizes the live status of each LangGraph agent as the pipeline runs.

export default function AgentPipeline({ agents }) {
  return (
    <div className="flex flex-wrap gap-2">
      {agents.map((agent) => (
        <div
          key={agent.name}
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            agent.status === "done"
              ? "bg-emerald-900 text-emerald-300"
              : agent.status === "running"
              ? "bg-amber-900 text-amber-300 animate-pulse"
              : "bg-slate-800 text-slate-400"
          }`}
        >
          {agent.name}
        </div>
      ))}
    </div>
  );
}
