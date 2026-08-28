// Generic dashboard layout wrapper: title + grid of children panels, reused by both pages.

export default function Dashboard({ title, children }) {
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">{title}</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">{children}</div>
    </div>
  );
}
