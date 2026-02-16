import { deleteQSO } from "../api";
import { QSO } from "../types";

interface Props {
  sessionId: string;
  qsos: QSO[];
  onDeleted: () => void;
}

export default function QSOTable({ sessionId, qsos, onDeleted }: Props) {
  const handleDelete = async (qsoId: string) => {
    await deleteQSO(sessionId, qsoId);
    onDeleted();
  };

  if (qsos.length === 0) {
    return <p>No QSOs logged yet.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>UTC</th>
          <th>Band</th>
          <th>Freq</th>
          <th>Mode</th>
          <th>Callsign</th>
          <th>RST S</th>
          <th>RST R</th>
          <th>Park</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {qsos.map((q, i) => (
          <tr key={q.id}>
            <td>{i + 1}</td>
            <td>{new Date(q.timestamp).toLocaleTimeString("en-GB", { timeZone: "UTC" })}</td>
            <td>{q.band}</td>
            <td>{q.frequency}</td>
            <td>{q.mode}</td>
            <td>{q.callsign}</td>
            <td>{q.rst_sent}</td>
            <td>{q.rst_received}</td>
            <td>{q.park_reference}</td>
            <td>
              <button onClick={() => handleDelete(q.id)} title="Delete">X</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
