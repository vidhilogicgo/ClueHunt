import { Gavel, Loader2 } from "lucide-react";

export default function AccusationPanel({ disabled, loading, onAccuse }) {
  return (
    <div className="sticky bottom-0 border-t border-panel/20 bg-night/92 px-4 py-4 text-paper shadow-dossier backdrop-blur">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="font-semibold text-paper/78">Review the scene and statements, then identify who lied.</p>
        <button
          className="inline-flex items-center justify-center gap-2 border border-paper/25 bg-brass px-5 py-3 font-black text-ink shadow-card transition hover:bg-paper disabled:cursor-not-allowed disabled:opacity-60"
          disabled={disabled || loading}
          onClick={onAccuse}
          type="button"
        >
          {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Gavel className="h-5 w-5" />}
          {loading ? "Evaluating..." : "Submit verdict"}
        </button>
      </div>
    </div>
  );
}
