// Consistent page header used at the top of every route.

export default function PageHeader({ eyebrow, title, subtitle, action }) {
  return (
    <div className="flex flex-col gap-4 border-b border-base-800/80 px-8 py-7 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow && (
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-brand-400">{eyebrow}</p>
        )}
        <h1 className="text-2xl font-bold tracking-tight text-base-50">{title}</h1>
        {subtitle && <p className="mt-1 max-w-2xl text-sm text-base-400">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
