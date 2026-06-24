export default function SectionTitle({ eyebrow, title, action }) {
  return (
    <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow ? <p className="text-xs font-black uppercase tracking-[0.26em] text-crimson">{eyebrow}</p> : null}
        <h2 className="font-display text-3xl font-black leading-tight text-ink">{title}</h2>
      </div>
      {action}
    </div>
  );
}
