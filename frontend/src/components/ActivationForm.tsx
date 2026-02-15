import React, { useEffect, useState } from "react";
import { createActivation, listActivations } from "../api";
import { Activation } from "../types";

interface Props {
  onSelect: (id: string) => void;
}

export default function ActivationForm({ onSelect }: Props) {
  const [activations, setActivations] = useState<Activation[]>([]);
  const [parkRef, setParkRef] = useState("");
  const [callsign, setCallsign] = useState("");

  useEffect(() => {
    listActivations().then(setActivations).catch(console.error);
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const activation = await createActivation({
      park_reference: parkRef.toUpperCase(),
      operator_callsign: callsign.toUpperCase(),
      start_time: new Date().toISOString(),
    });
    onSelect(activation.id);
  };

  return (
    <div>
      <h2>Start New Activation</h2>
      <form onSubmit={handleCreate} style={{ display: "flex", gap: "0.5rem", alignItems: "end", flexWrap: "wrap" }}>
        <label>
          Park Reference
          <input
            value={parkRef}
            onChange={(e) => setParkRef(e.target.value)}
            placeholder="K-0001"
            required
          />
        </label>
        <label>
          Operator Callsign
          <input
            value={callsign}
            onChange={(e) => setCallsign(e.target.value)}
            placeholder="W1ABC"
            required
          />
        </label>
        <button type="submit">Start Activation</button>
      </form>

      {activations.length > 0 && (
        <>
          <h2 style={{ marginTop: "1.5rem" }}>Previous Activations</h2>
          <table>
            <thead>
              <tr>
                <th>Park</th>
                <th>Callsign</th>
                <th>Date</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {activations.map((a) => (
                <tr key={a.id}>
                  <td>{a.park_reference}</td>
                  <td>{a.operator_callsign}</td>
                  <td>{new Date(a.start_time).toLocaleDateString()}</td>
                  <td>
                    <button onClick={() => onSelect(a.id)}>Open</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}
