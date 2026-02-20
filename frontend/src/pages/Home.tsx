import { useEffect, useState, useCallback } from "react";
import { getTodaySession, getSession, getSettings } from "../api";
import { HuntSessionDetail, Settings, Spot } from "../types";
import SettingsForm from "../components/SettingsForm";
import SpotsList from "../components/SpotsList";
import QSOForm from "../components/QSOForm";
import QSOTable from "../components/QSOTable";
import ExportButton from "../components/ExportButton";

export default function Home() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState<HuntSessionDetail | null>(null);
  const [selectedSpot, setSelectedSpot] = useState<Spot | null>(null);
  const [spotsRefresh, setSpotsRefresh] = useState(0);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    getSettings()
      .then((s) => {
        setSettings(s);
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
    setSpotsRefresh((n) => n + 1);
  }, [session]);

  useEffect(() => {
    if (settings?.operator_callsign) {
      getTodaySession().then(setSession).catch(console.error);
    }
  }, [settings?.operator_callsign]);

  if (loading) return <p>Loading...</p>;

  if (!settings?.operator_callsign) {
    return (
      <div>
        <h1>POTA Hunter Logger</h1>
        <SettingsForm
          onSaved={(saved) => {
            setSettings(saved);
          }}
        />
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
            <span>{settings.operator_callsign}</span>
            <span>{session.qsos.length} QSOs</span>
            <ExportButton sessionId={session.id} />
            <button onClick={() => setShowSettings((v) => !v)} style={{ marginLeft: "auto" }}>
              Settings
            </button>
          </div>
          {showSettings && (
            <SettingsForm
              currentSettings={settings}
              onSaved={(saved) => {
                setSettings(saved);
                setShowSettings(false);
              }}
              onCancel={() => setShowSettings(false)}
            />
          )}
          <SpotsList onSelect={setSelectedSpot} refreshToken={spotsRefresh} />
          <QSOForm sessionId={session.id} onCreated={loadSession} selectedSpot={selectedSpot} />
          <QSOTable sessionId={session.id} qsos={session.qsos} onDeleted={loadSession} />
        </>
      )}
    </div>
  );
}
