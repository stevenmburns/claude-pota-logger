import React, { useState } from "react";
import { updateSettings } from "../api";
import { Settings } from "../types";

interface Props {
  onSaved: (settings: Settings) => void;
  currentSettings?: Settings;
  onCancel?: () => void;
}

export default function SettingsForm({ onSaved, currentSettings, onCancel }: Props) {
  const [callsign, setCallsign] = useState(currentSettings?.operator_callsign ?? "");
  const [flrigHost, setFlrigHost] = useState(currentSettings?.flrig_host ?? "host.docker.internal");
  const [flrigPort, setFlrigPort] = useState(currentSettings?.flrig_port ?? 12345);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const upper = callsign.toUpperCase().trim();
    if (!upper) return;
    const saved = await updateSettings(upper, flrigHost, flrigPort);
    onSaved(saved);
  };

  const isInitial = !currentSettings;

  return (
    <div>
      {isInitial && (
        <>
          <h2>Welcome to POTA Hunter Logger</h2>
          <p>Enter your operator callsign to get started.</p>
        </>
      )}
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.5rem", maxWidth: "400px" }}>
        <label>
          Operator Callsign
          <input
            value={callsign}
            onChange={(e) => setCallsign(e.target.value)}
            placeholder="W1ABC"
            required
            autoFocus
          />
        </label>
        <label>
          flrig Host
          <input
            value={flrigHost}
            onChange={(e) => setFlrigHost(e.target.value)}
            placeholder="host.docker.internal"
          />
        </label>
        <label>
          flrig Port
          <input
            type="number"
            value={flrigPort}
            onChange={(e) => setFlrigPort(parseInt(e.target.value, 10))}
            min={1}
            max={65535}
          />
        </label>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button type="submit">Save</button>
          {onCancel && <button type="button" onClick={onCancel}>Cancel</button>}
        </div>
      </form>
    </div>
  );
}
