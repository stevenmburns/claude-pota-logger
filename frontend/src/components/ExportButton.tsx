import { exportUrl } from "../api";

interface Props {
  activationId: string;
}

export default function ExportButton({ activationId }: Props) {
  return (
    <a href={exportUrl(activationId)} download>
      <button type="button">Export ADIF</button>
    </a>
  );
}
