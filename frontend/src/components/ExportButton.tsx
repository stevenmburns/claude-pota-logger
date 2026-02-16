import { exportUrl } from "../api";

interface Props {
  sessionId: string;
}

export default function ExportButton({ sessionId }: Props) {
  return (
    <a href={exportUrl(sessionId)} download>
      <button type="button">Export ADIF</button>
    </a>
  );
}
