import { useEffect, useState, useCallback } from "react";
import { getTodaySession, getSession, getSettings } from "../api";
import { HuntSessionDetail } from "../types";
import SettingsForm from "../components/SettingsForm";
import QSOForm from "../components/QSOForm";
import QSOTable from "../components/QSOTable";
import ExportButton from "../components/ExportButton";

export default function Home() {
  const [operatorCallsign, setOperatorCallsign] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<HuntSessionDetail | null>(null);

  useEffect(() => {
    getSettings()
      .then((s) => {
        setOperatorCallsign(s.operator_callsign || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const loadSession = useCallback(() => {
    if (session) {
      getSession(session.id).then(setSession).catch(console.error);
    } else {
      getTodaySession().then(setSession).catch(console.error);
    }
  }, [session]);

  useEffect(() => {
    if (operatorCallsign) {
      getTodaySession().then(setSession).catch(console.error);
    }
  }, [operatorCallsign]);

  if (loading) return <p>Loading...</p>;

  if (!operatorCallsign) {
    return (
      <div>
        <h1>POTA Hunter Logger</h1>
        <SettingsForm onSaved={setOperatorCallsign} />
      </div>
    );
  }

  return (
    <div>
      <h1>POTA Hunter Logger</h1>
      {session && (
        <>
          <div style={{ display: "flex", gap: "1rem", alignItems: "center", marginBottom: "1rem" }}>
            <strong>{session.session_date}</strong>
            <span>{operatorCallsign}</span>
            <span>{session.qsos.length} QSOs</span>
            <ExportButton sessionId={session.id} />
          </div>
          <QSOForm sessionId={session.id} onCreated={loadSession} />
          <QSOTable sessionId={session.id} qsos={session.qsos} onDeleted={loadSession} />
        </>
      )}
    </div>
  );
}
