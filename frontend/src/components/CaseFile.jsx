import { BadgeAlert, Fingerprint, RefreshCw } from "lucide-react";

export default function CaseFile({ mystery, onNewCase }) {
  return (
    <section className="px-4 pt-10 text-ink">
      <div className="mx-auto max-w-7xl">
        <div className="case-board p-5 pt-8 sm:p-7 sm:pt-10">
          <div className="grid gap-6 lg:grid-cols-[1fr_320px] lg:items-start">
            <div>
              <p className="mb-2 text-xs font-black uppercase tracking-[0.28em] text-wax">Case File {mystery.id}</p>
              <h1 className="font-display max-w-4xl text-4xl font-black leading-tight text-ink sm:text-6xl">{mystery.title}</h1>
              <div className="case-note mt-5 rotate-[-0.5deg] border-l-4 border-crimson p-4">
                <p className="text-xs font-black uppercase tracking-[0.26em] text-crimson">Incident</p>
                <h2 className="font-display text-3xl font-black capitalize leading-tight text-ink">{mystery.case_type}</h2>
                <p className="text-base font-semibold leading-8 text-ink/76">{mystery.crime_story}</p>
                <p className="mt-4 border-t border-ink/10 pt-3 text-sm font-black uppercase tracking-[0.16em] text-crimson">
                  Three suspects gave statements. One of them is lying.
                </p>
              </div>
            </div>

            <div className="grid gap-3">
              <button
                className="inline-flex items-center justify-center gap-2 border border-ink/30 bg-[#f1d49a] px-4 py-3 font-black text-ink shadow-card transition hover:border-crimson hover:text-crimson"
                onClick={onNewCase}
              >
                <RefreshCw className="h-5 w-5" />
                New case
              </button>
              <div className="case-note p-4 text-ink">
                <div className="mb-3 flex items-center gap-2">
                  <BadgeAlert className="h-5 w-5 text-crimson" />
                  <p className="font-black uppercase tracking-[0.14em]">Victim</p>
                </div>
                <p className="font-semibold text-ink/78">{mystery.victim}</p>
              </div>
              <div className="bg-crimson p-4 text-paper shadow-card">
                <div className="mb-3 flex items-center gap-2">
                  <Fingerprint className="h-5 w-5 text-paper" />
                  <p className="font-black uppercase tracking-[0.14em]">Difficulty</p>
                </div>
                <p className="capitalize text-paper/90">{mystery.difficulty}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
