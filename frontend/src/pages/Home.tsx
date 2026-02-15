import { useEffect, useState, useCallback } from "react";
import { getActivation } from "../api";
import { ActivationDetail } from "../types";
import ActivationForm from "../components/ActivationForm";
import QSOForm from "../components/QSOForm";
import QSOTable from "../components/QSOTable";
import ExportButton from "../components/ExportButton";

export default function Home() {
  const [activationId, setActivationId] = useState<string | null>(null);
  const [activation, setActivation] = useState<ActivationDetail | null>(null);

  const refresh = useCallback(() => {
    if (activationId) {
      getActivation(activationId).then(setActivation).catch(console.error);
    }
  }, [activationId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  if (!activationId || !activation) {
    return (
      <div>
        <h1>POTA Logger</h1>
        <ActivationForm onSelect={setActivationId} />
      </div>
    );
  }

  return (
    <div>
      <h1>POTA Logger</h1>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "1rem" }}>
        <strong>{activation.park_reference}</strong>
        <span>{activation.operator_callsign}</span>
        <span>{new Date(activation.start_time).toLocaleDateString()}</span>
        <span>{activation.qsos.length} QSOs</span>
        <ExportButton activationId={activationId} />
        <button onClick={() => { setActivationId(null); setActivation(null); }}>
          Back
        </button>
      </div>
      <QSOForm activationId={activationId} onCreated={refresh} />
      <QSOTable activationId={activationId} qsos={activation.qsos} onDeleted={refresh} />
    </div>
  );
}
