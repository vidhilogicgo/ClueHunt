import { useState } from "react";
import AccusationPanel from "./components/AccusationPanel.jsx";
import CaseFile from "./components/CaseFile.jsx";
import CaseSetup from "./components/CaseSetup.jsx";
import InvestigationBoard from "./components/InvestigationBoard.jsx";
import VerdictModal from "./components/VerdictModal.jsx";
import { createCase, submitAccusation } from "./api.js";

export default function App() {
  const [mystery, setMystery] = useState(null);
  const [selectedSuspect, setSelectedSuspect] = useState("");
  const [verdict, setVerdict] = useState(null);
  const [loadingCase, setLoadingCase] = useState(false);
  const [loadingVerdict, setLoadingVerdict] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate(payload) {
    setError("");
    setLoadingCase(true);
    setVerdict(null);
    setSelectedSuspect("");
    try {
      setMystery(await createCase(payload));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingCase(false);
    }
  }

  async function handleAccuse() {
    if (!mystery || !selectedSuspect) {
      return;
    }
    setError("");
    setLoadingVerdict(true);
    try {
      setVerdict(
        await submitAccusation({
          case_id: mystery.id,
          suspect_id: selectedSuspect,
          player_name: "Detective",
        }),
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingVerdict(false);
    }
  }

  if (!mystery) {
    return (
      <div className="detective-bg min-h-screen">
        <CaseSetup loading={loadingCase} onGenerate={handleGenerate} />
        {error ? <p className="fixed bottom-4 left-1/2 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 bg-crimson p-3 text-center font-bold text-panel">{error}</p> : null}
      </div>
    );
  }

  return (
    <div className="case-shell min-h-screen">
      <CaseFile mystery={mystery} onNewCase={() => setMystery(null)} />
      {error ? <p className="mx-auto mt-4 max-w-7xl bg-crimson px-4 py-3 font-bold text-panel">{error}</p> : null}
      <InvestigationBoard mystery={mystery} onSelectSuspect={setSelectedSuspect} selectedSuspect={selectedSuspect} />
      <AccusationPanel disabled={!selectedSuspect} loading={loadingVerdict} onAccuse={handleAccuse} />
      <VerdictModal onClose={() => setVerdict(null)} result={verdict} suspects={mystery.suspects} />
    </div>
  );
}
