import { CheckCircle2, XCircle } from "lucide-react";

export default function VerdictModal({ result, suspects, onClose }) {
  if (!result) {
    return null;
  }

  const selected = suspects.find((suspect) => suspect.id === result.selected_suspect_id);
  const correct = suspects.find((suspect) => suspect.id === result.correct_suspect_id);
  const Icon = result.is_correct ? CheckCircle2 : XCircle;

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-[#1f120c]/72 px-4 py-6 backdrop-blur-sm">
      <section className="case-board max-h-[90vh] w-full max-w-3xl overflow-auto p-5 shadow-dossier">
        <div className="mb-4 flex items-start gap-3 border-b border-ink/15 pb-4">
          <Icon className={`mt-1 h-7 w-7 shrink-0 ${result.is_correct ? "text-green-700" : "text-crimson"}`} />
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-crimson">Final Verdict</p>
            <h2 className="text-3xl font-black text-ink">{result.is_correct ? "Case solved" : "Case remains open"}</h2>
          </div>
        </div>

        <div className="mb-5 grid gap-3 sm:grid-cols-2">
          <div className="case-note p-3">
            <p className="text-xs font-bold uppercase text-ink/50">You marked</p>
            <p className="font-black text-ink">{selected?.name || "Unknown"}</p>
          </div>
          <div className="case-note p-3">
            <p className="text-xs font-bold uppercase text-ink/50">Actual liar</p>
            <p className="font-black text-ink">{correct?.name || "Unknown"}</p>
          </div>
        </div>

        <p className="whitespace-pre-line leading-8 text-ink/78">{result.explanation}</p>

        <button className="mt-6 bg-crimson px-5 py-3 font-bold text-paper transition hover:bg-wax" onClick={onClose}>
          Return to board
        </button>
      </section>
    </div>
  );
}
