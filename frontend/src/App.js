import React, { useState } from "react";
import PestelForm from "./components/PestelForm";
import ResultsDisplay from "./components/ResultsDisplay";

function App() {
  const [results, setResults] = useState(null);

  return (
    <div>
      <PestelForm onResults={setResults} />
      <ResultsDisplay results={results} />
    </div>
  );
}

export default App;
