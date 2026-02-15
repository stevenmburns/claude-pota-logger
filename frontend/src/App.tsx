import Home from "./pages/Home";

const globalStyles = `
  * { box-sizing: border-box; }
  body { font-family: system-ui, sans-serif; margin: 0; padding: 1rem; background: #f5f5f5; }
  h1 { margin-top: 0; }
  label { display: flex; flex-direction: column; font-size: 0.85rem; font-weight: 600; }
  input, select { padding: 0.4rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.95rem; }
  button { padding: 0.4rem 0.8rem; border: none; border-radius: 4px; background: #2563eb; color: white; cursor: pointer; font-size: 0.95rem; }
  button:hover { background: #1d4ed8; }
  table { border-collapse: collapse; width: 100%; margin-top: 1rem; }
  th, td { text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #ddd; }
  th { background: #e5e7eb; }
  a { text-decoration: none; }
`;

export default function App() {
  return (
    <>
      <style>{globalStyles}</style>
      <Home />
    </>
  );
}
