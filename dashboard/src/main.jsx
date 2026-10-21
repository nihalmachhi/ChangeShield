import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const PATHS = { analyze: "/api/v1/analyses" };
const initialLinks = ["Client → Edge", "Edge → Service"];

function App() {
  const [candidateHealthy, setCandidateHealthy] = useState(false);
  const [report, setReport] = useState(null);
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");

  async function analyze() {
    setMessage("Connecting to the local ChangeShield API…");
    try {
      const response = await fetch(`http://127.0.0.1:8010${PATHS.analyze}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: "Edge maintenance", before: { nodes: ["client", "edge", "service"], links: [{ source: "client", target: "edge" }, { source: "edge", target: "service" }] }, after: { nodes: ["client", "edge", "service"], links: candidateHealthy ? [{ source: "client", target: "edge" }, { source: "edge", target: "service" }] : [{ source: "client", target: "edge" }] }, intents: [{ name: "Client access to service", source: "client", destination: "service", property: "reachable", critical: true }] }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail || `API returned ${response.status}`);
      setReport(body);
      setMessage("Live analysis complete.");
    } catch (error) {
      setMessage(`${error.message}. Showing the local example instead.`);
    }
  }

  const reachable = candidateHealthy;
  return <main>
    <header><a className="brand" href="#top"><span className="mark">CS</span> ChangeShield</a><span className="eyebrow">NETWORK CHANGE REVIEW</span><a href="#method">Method</a></header>
    <section className="hero" id="top"><p className="eyebrow">PRE-DEPLOYMENT CHECK · READ ONLY</p><h1>Know what a change<br/><em>breaks before rollout.</em></h1><p>Compare a proposed network change with declared service intent. Follow the path evidence before you decide.</p></section>
    <section className="workspace" aria-label="Interactive change review">
      <div className="panel topology"><div className="panel-head"><div><p className="eyebrow">01 / CANDIDATE TOPOLOGY</p><h2>Edge maintenance</h2></div><span className="pill">Demo data</span></div>
        <p className="subtle">Toggle the edge-to-service link to see the impact on the declared intent.</p>
        <div className="network" aria-label="Client connected to Edge, with an optional Edge to Service link"><div className="node"><span>CLIENT</span><b>Client</b></div><span className="wire active"/><div className="node"><span>EDGE</span><b>Edge</b></div><button className={`wire-toggle ${candidateHealthy ? "on" : "off"}`} aria-label="Toggle edge-to-service link" aria-pressed={candidateHealthy} onClick={() => { setCandidateHealthy(!candidateHealthy); setReport(null); }}>↔</button><div className={`node ${reachable ? "" : "dim"}`}><span>SERVICE</span><b>Service</b></div></div>
        <button className="button" onClick={analyze}>Analyze with local API</button>
        <label className="token">Optional analyst token<input type="password" value={token} onChange={event => setToken(event.target.value)} placeholder="local analyst token" autoComplete="off"/></label>
        {message && <p role="status" className="subtle">{message}</p>}
      </div>
      <aside className={`panel result ${reachable ? "good" : "bad"}`} aria-live="polite"><p className="eyebrow">02 / INTENT CHECK</p><div className="verdict"><span className="status-dot"/><h2>{report?.verdict || (reachable ? "Intent preserved" : "Reachability lost")}</h2></div><p className="subtle">Client must remain reachable to Service during the change.</p><div className="path-row"><span>BEFORE</span><b>{initialLinks.join("  /  ")}</b></div><div className="path-row"><span>AFTER</span><b>{reachable ? initialLinks.join("  /  ") : "No path found"}</b></div><div className="confidence"><span>Example confidence</span><strong>{report ? `${Math.round(report.confidence * 100)}%` : "94%"}</strong></div><p className="footnote">Unsupported configuration can lower confidence. This review never deploys or changes a device.</p></aside>
    </section>
    <section className="method" id="method"><p className="eyebrow">HOW THE RESULT IS MADE</p><h2>Model the links. Check the promise.</h2><p>ChangeShield compares topology snapshots, searches for an intent path, and exposes unsupported input so reviewers can judge the evidence.</p><div className="steps"><span>1. Before &amp; after</span><span>2. Path search</span><span>3. Intent verdict</span></div></section>
    <footer>ChangeShield <span>Local analysis · No device writes</span></footer>
  </main>;
}

createRoot(document.getElementById("root")).render(<App/>);
