import { MapPinned, ShieldQuestion } from "lucide-react";
import SectionTitle from "./SectionTitle.jsx";

function SceneCard({ scene, index }) {
  return (
    <article className="case-note relative flex h-full flex-col p-5 transition hover:-translate-y-1">
      <div className="mb-4 flex items-start justify-between gap-3 border-b border-ink/10 pb-4">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center bg-crimson text-paper">
          <MapPinned className="h-5 w-5" />
        </div>
        <span className="font-display text-4xl font-black leading-none text-crimson/35">{String(index + 1).padStart(2, "0")}</span>
      </div>
      <div className="mb-3">
        <h3 className="font-display text-2xl font-black leading-tight text-ink">{scene.title}</h3>
        <p className="mt-1 text-sm font-extrabold uppercase tracking-[0.16em] text-crimson">{scene.character_name}</p>
      </div>
      <p className="flex-1 font-semibold leading-7 text-ink/74">{scene.description}</p>
      <p className="mt-5 bg-ink/5 px-3 py-2 text-sm font-bold text-ink/58">{scene.atmosphere}</p>
    </article>
  );
}

function SuspectCard({ suspect, selected, onSelect, index }) {
  return (
    <button
      className={`group h-full min-h-[132px] border p-5 text-left shadow-card transition ${
        selected ? "border-wax bg-crimson text-paper" : "case-note border-ink/25 text-ink hover:-translate-y-1 hover:border-crimson"
      }`}
      onClick={() => onSelect(suspect.id)}
      type="button"
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className={`mb-1 text-xs font-black uppercase tracking-[0.18em] ${selected ? "text-panel/70" : "text-crimson"}`}>
            Statement {index + 1}
          </p>
          <h3 className="font-display text-2xl font-black leading-tight">{suspect.name}</h3>
          <p className={selected ? "font-semibold text-paper/78" : "font-semibold text-ink/55"}>{suspect.role}</p>
        </div>
        <div className={`flex h-9 w-9 shrink-0 items-center justify-center border ${selected ? "border-paper/30 bg-paper/10" : "border-ink/15 bg-crimson/5 group-hover:border-crimson"}`}>
          <ShieldQuestion className="h-5 w-5" />
        </div>
      </div>
      <div className={`border-l-4 pl-3 ${selected ? "border-panel/40" : "border-crimson/35"}`}>
        <p className={`mb-1 text-[11px] font-black uppercase tracking-[0.18em] ${selected ? "text-paper/60" : "text-ink/45"}`}>
          Statement
        </p>
        <p className={`text-sm font-bold leading-7 ${selected ? "text-paper/86" : "text-ink/70"}`}>
          {suspect.statement || "No statement recorded. Generate a new case to continue the interrogation format."}
        </p>
      </div>
      <p className={`mt-4 text-xs font-black uppercase tracking-[0.18em] ${selected ? "text-paper/70" : "text-crimson"}`}>
        {selected ? "Marked as the lie" : "Mark this as the lie"}
      </p>
    </button>
  );
}

export default function InvestigationBoard({ mystery, selectedSuspect, onSelectSuspect }) {
  return (
    <main className="mx-auto max-w-7xl px-4 py-10">
      <section className="case-band p-4 sm:p-6">
        <SectionTitle eyebrow="Scenes" title="Investigation board" />
        <div className="grid gap-4 xl:grid-cols-3">
          {mystery.scenes.map((scene, index) => (
            <SceneCard index={index} key={scene.id} scene={scene} />
          ))}
        </div>
      </section>

      <section className="case-band mt-8 p-4 sm:p-6">
        <SectionTitle eyebrow="Interrogation" title="Who is lying?" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {mystery.suspects.map((suspect, index) => (
            <SuspectCard
              index={index}
              key={suspect.id}
              onSelect={onSelectSuspect}
              selected={selectedSuspect === suspect.id}
              suspect={suspect}
            />
          ))}
        </div>
      </section>
    </main>
  );
}
