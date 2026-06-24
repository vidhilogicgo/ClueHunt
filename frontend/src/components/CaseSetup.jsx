import { FilePlus2, Loader2, Search, Sparkles, Target } from "lucide-react";

export default function CaseSetup({ onGenerate, loading }) {
  function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onGenerate({
      difficulty: form.get("difficulty"),
    });
  }

  return (
    <section className="relative mx-auto flex min-h-screen w-full max-w-7xl flex-col justify-center gap-10 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex w-full flex-col items-center text-center text-paper">
        <div className="mb-5 inline-flex items-center gap-2 border border-panel/30 bg-night/60 px-3 py-2 text-xs font-black uppercase tracking-[0.24em] text-panel shadow-card backdrop-blur">
          <Search className="h-4 w-4" />
          AI Detective Desk
        </div>
        <h1 className="font-display max-w-full text-5xl font-black leading-none text-paper drop-shadow-[0_5px_0_rgba(30,12,6,0.45)] sm:text-7xl lg:text-9xl">
          ClueHunt
        </h1>
        <p className="mt-5 max-w-4xl text-base font-semibold leading-8 text-paper/82 sm:text-lg">
          Study the scene. Catch the lie.
        </p>
        <div className="mt-8 grid w-full max-w-5xl grid-cols-1 gap-2 border border-panel/20 bg-night/45 p-2 shadow-dossier backdrop-blur sm:grid-cols-3">
          {["Scene", "Statements", "Verdict"].map((item) => (
            <div className="case-note px-3 py-3 text-center text-xs font-black uppercase tracking-[0.18em] text-night" key={item}>
              {item}
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="case-board relative mx-auto w-full max-w-6xl overflow-visible p-5 pt-8 sm:p-7 sm:pt-10 lg:p-8 lg:pt-10">
        <div className="binding-tab absolute -left-10 top-12 hidden h-40 w-10 items-center justify-center px-2 text-center text-xs font-black uppercase tracking-[0.16em] [writing-mode:vertical-rl] lg:flex">
          Case Report
        </div>
        <div className="absolute right-5 top-5 flex h-12 w-12 items-center justify-center border border-paper/30 bg-crimson text-paper shadow-card">
          <Target className="h-6 w-6" />
        </div>
        <div className="case-note mb-6 rotate-[-0.5deg] border-b border-ink/15 p-4 pr-16 sm:p-5">
          <p className="text-xs font-black uppercase tracking-[0.22em] text-crimson">New Case</p>
          <h2 className="font-display text-2xl font-black leading-tight text-ink sm:text-3xl lg:text-4xl">Open an investigation</h2>
        </div>

        <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
          <label className="case-note block p-4 sm:p-5">
            <span className="mb-2 block text-sm font-bold text-ink">Difficulty</span>
            <select className="w-full border border-ink/30 bg-[#f7e4b8] px-4 py-3 font-bold text-ink outline-none transition focus:border-crimson focus:ring-2 focus:ring-crimson/20" name="difficulty">
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>

          <button
            className="flex min-h-[96px] w-full items-center justify-center gap-2 border border-paper/20 bg-crimson px-4 py-3 font-black text-paper shadow-card transition hover:bg-wax disabled:cursor-not-allowed disabled:opacity-60"
            disabled={loading}
            type="submit"
          >
            {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <FilePlus2 className="h-5 w-5" />}
            {loading ? "Generating case..." : "Generate case file"}
          </button>
        </div>

      </form>
    </section>
  );
}
