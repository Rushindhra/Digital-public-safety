"use client";

import { useCallback, useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  Bot,
  FileWarning,
  IndianRupee,
  Landmark,
  MapPinned,
  Moon,
  Network,
  ShieldCheck,
  Sun,
  Upload,
} from "lucide-react";
import {
  login,
  analyseScam,
  fetchReports,
  fetchAnalytics,
  fetchHotspots,
  analyseGraph,
  chatAssistant,
  createReport,
  analyseCounterfeit,
} from "../lib/api";

type Tab =
  | "shield"
  | "scam"
  | "counterfeit"
  | "graph"
  | "geo"
  | "cases"
  | "analytics";

const TABS: { id: Tab; label: string; icon: typeof Bot }[] = [
  { id: "shield", label: "Citizen Shield", icon: Bot },
  { id: "scam", label: "Arrest Scam", icon: AlertTriangle },
  { id: "counterfeit", label: "Currency", icon: IndianRupee },
  { id: "graph", label: "Fraud Network", icon: Network },
  { id: "geo", label: "Geospatial", icon: MapPinned },
  { id: "cases", label: "Cases", icon: FileWarning },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function Dashboard() {
  const [dark, setDark] = useState(false);
  const [tab, setTab] = useState<Tab>("scam");
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("admin@suraksha.gov.in");
  const [password, setPassword] = useState("Admin@12345");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [scamText, setScamText] = useState(
    "Your CBI officer says you are under digital arrest. Do not disconnect and transfer money to the safe account immediately."
  );
  const [scamResult, setScamResult] = useState<Record<string, unknown> | null>(null);

  const [chatMsg, setChatMsg] = useState("Is this SMS about digital arrest a scam?");
  const [chatReply, setChatReply] = useState("");

  const [reports, setReports] = useState<Record<string, unknown>[]>([]);
  const [analytics, setAnalytics] = useState<Record<string, unknown> | null>(null);
  const [hotspots, setHotspots] = useState<Record<string, unknown>[]>([]);
  const [graphResult, setGraphResult] = useState<Record<string, unknown> | null>(null);
  const [counterfeitResult, setCounterfeitResult] = useState<Record<string, unknown> | null>(null);

  const [newReport, setNewReport] = useState({
    category: "digital_arrest",
    title: "",
    description: "",
    district: "",
  });

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  const handleLogin = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      const pair = await login(email, password);
      setToken(pair.access_token);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Login failed");
    } finally {
      setBusy(false);
    }
  }, [email, password]);

  const requireAuth = useCallback(() => {
    if (!token) {
      setError("Sign in first to use protected intelligence services.");
      return false;
    }
    return true;
  }, [token]);

  const runScam = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    setError("");
    try {
      setScamResult((await analyseScam(token, scamText)) as Record<string, unknown>);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setBusy(false);
    }
  };

  const runChat = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    setError("");
    try {
      const res = (await chatAssistant(token, chatMsg)) as { reply: string };
      setChatReply(res.reply);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Assistant failed");
    } finally {
      setBusy(false);
    }
  };

  const loadCases = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    setError("");
    try {
      setReports((await fetchReports(token)) as Record<string, unknown>[]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load reports");
    } finally {
      setBusy(false);
    }
  };

  const submitReport = async () => {
    if (!requireAuth()) return;
    const title = newReport.title.trim();
    const description = newReport.description.trim();
    const district = newReport.district.trim();
    if (title.length < 3) {
      setError("Please enter a report title with at least 3 characters.");
      return;
    }
    if (description.length < 10) {
      setError("Please describe the incident in at least 10 characters.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      await createReport(token, { ...newReport, title, description, district });
      setNewReport({ category: "digital_arrest", title: "", description: "", district: "" });
      await loadCases();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to submit report");
    } finally {
      setBusy(false);
    }
  };

  const loadAnalytics = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    try {
      setAnalytics((await fetchAnalytics(token)) as Record<string, unknown>);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Analytics failed");
    } finally {
      setBusy(false);
    }
  };

  const loadHotspots = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    try {
      setHotspots((await fetchHotspots(token)) as Record<string, unknown>[]);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Hotspots failed");
    } finally {
      setBusy(false);
    }
  };

  const runGraph = async () => {
    if (!requireAuth()) return;
    setBusy(true);
    try {
      const nodes = [
        { id: "victim_1", type: "victim" },
        { id: "phone_91", type: "phone" },
        { id: "upi_mule", type: "account" },
        { id: "bank_ac", type: "bank" },
      ];
      const edges = [
        { source: "victim_1", target: "phone_91" },
        { source: "phone_91", target: "upi_mule" },
        { source: "upi_mule", target: "bank_ac" },
      ];
      setGraphResult((await analyseGraph(token, nodes, edges)) as Record<string, unknown>);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Graph analysis failed");
    } finally {
      setBusy(false);
    }
  };

  const onCounterfeitUpload = async (file: File) => {
    if (!requireAuth()) return;
    setBusy(true);
    setError("");
    try {
      setCounterfeitResult(
        (await analyseCounterfeit(token, file, 500)) as Record<string, unknown>
      );
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Counterfeit analysis failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="app">
      <header>
        <div className="brand">
          <div className="emblem">
            <Landmark size={24} />
          </div>
          <div>
            <b>सुरक्षा सेतु</b>
            <span>Government of India · Digital Public Safety</span>
          </div>
        </div>
        <div className="header-actions">
          <button className="icon-btn" onClick={() => setDark((d) => !d)} aria-label="Toggle theme">
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <div className="status">
            <i /> NATIONAL COMMAND NETWORK ONLINE
          </div>
        </div>
      </header>

      <section className="hero compact">
        <div>
          <p className="eyebrow">AI FOR A SAFER DIGITAL INDIA</p>
          <h1>
            Detect fraud before
            <br />
            <em>it becomes a crisis.</em>
          </h1>
          <div className="numbers">
            <div>
              <b>1930</b>
              <span>Cyber Fraud Helpline</span>
            </div>
            <div>
              <b>112</b>
              <span>Emergency Response</span>
            </div>
            <div>
              <b>MongoDB</b>
              <span>Live Intelligence Store</span>
            </div>
          </div>
        </div>
        <div className="shield">
          <ShieldCheck size={120} />
        </div>
      </section>

      <nav className="tabs">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={tab === id ? "active" : ""}
            onClick={() => setTab(id)}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      <section className="workspace full">
        <div className="panel main-panel">
          {tab === "scam" && (
            <>
              <div className="panelTitle">
                <AlertTriangle /> Digital Arrest Scam Detection
              </div>
              <textarea
                value={scamText}
                onChange={(e) => setScamText(e.target.value)}
                aria-label="Message to analyse"
              />
              <button onClick={runScam} disabled={busy}>
                Analyse threat
              </button>
              {scamResult && (
                <div className={`result ${scamResult.risk_level as string}`}>
                  <b>
                    {String(scamResult.risk_level).toUpperCase()} RISK ·{" "}
                    {scamResult.risk_score as number}/100
                  </b>
                  <p>{scamResult.explanation as string}</p>
                  <ul>
                    {(scamResult.suggested_actions as string[])?.map((x) => (
                      <li key={x}>{x}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}

          {tab === "shield" && (
            <>
              <div className="panelTitle">
                <Bot /> Citizen Fraud Shield
              </div>
              <textarea
                value={chatMsg}
                onChange={(e) => setChatMsg(e.target.value)}
                aria-label="Ask the assistant"
              />
              <button onClick={runChat} disabled={busy}>
                Ask assistant
              </button>
              {chatReply && <div className="result low"><p>{chatReply}</p></div>}
            </>
          )}

          {tab === "counterfeit" && (
            <>
              <div className="panelTitle">
                <IndianRupee /> Counterfeit Currency Detection
              </div>
              <label className="upload-zone">
                <Upload size={20} />
                Upload INR note image (JPEG/PNG)
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) onCounterfeitUpload(f);
                  }}
                />
              </label>
              {counterfeitResult && (
                <div className="result">
                  <b>
                    Probability:{" "}
                    {Math.round(
                      (counterfeitResult.counterfeit_probability as number) * 100
                    )}
                    %
                  </b>
                  <p>{counterfeitResult.verdict as string}</p>
                </div>
              )}
            </>
          )}

          {tab === "graph" && (
            <>
              <div className="panelTitle">
                <Network /> Fraud Network Graph
              </div>
              <p className="muted">
                Analyse victim → phone → account → bank chains to find mules and masterminds.
              </p>
              <button onClick={runGraph} disabled={busy}>
                Run network analysis
              </button>
              {graphResult && (
                <pre className="code-block">{JSON.stringify(graphResult, null, 2)}</pre>
              )}
            </>
          )}

          {tab === "geo" && (
            <>
              <div className="panelTitle">
                <MapPinned /> Geospatial Hotspots
              </div>
              <button onClick={loadHotspots} disabled={busy}>
                Load district hotspots
              </button>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>District</th>
                      <th>Incidents</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {hotspots.map((h) => (
                      <tr key={String(h.district)}>
                        <td>{String(h.district)}</td>
                        <td>{String(h.incidents)}</td>
                        <td>{String(h.risk_score)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {tab === "cases" && (
            <>
              <div className="panelTitle">
                <FileWarning /> Case Management
              </div>
              <button onClick={loadCases} disabled={busy}>
                Refresh reports
              </button>
              <div className="form-grid">
                <input
                  placeholder="Report title"
                  value={newReport.title}
                  onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                />
                <input
                  placeholder="District"
                  value={newReport.district}
                  onChange={(e) => setNewReport({ ...newReport, district: e.target.value })}
                />
                <textarea
                  placeholder="Description"
                  value={newReport.description}
                  onChange={(e) =>
                    setNewReport({ ...newReport, description: e.target.value })
                  }
                />
                <button onClick={submitReport} disabled={busy}>
                  Submit report
                </button>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map((r) => (
                      <tr key={String(r.id)}>
                        <td>{String(r.title)}</td>
                        <td>{String(r.category)}</td>
                        <td>{String(r.status)}</td>
                        <td>{String(r.risk_score)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {tab === "analytics" && (
            <>
              <div className="panelTitle">
                <BarChart3 /> Analytics Dashboard
              </div>
              <button onClick={loadAnalytics} disabled={busy}>
                Load analytics
              </button>
              {analytics && (
                <div className="stats-grid">
                  <div className="stat">
                    <b>{analytics.total_reports as number}</b>
                    <span>Total reports</span>
                  </div>
                  <div className="stat">
                    <b>{analytics.reports_30d as number}</b>
                    <span>Last 30 days</span>
                  </div>
                  <div className="stat">
                    <b>{analytics.average_risk as number}</b>
                    <span>Avg risk score</span>
                  </div>
                </div>
              )}
              {analytics && (
                <pre className="code-block">
                  {JSON.stringify(analytics.by_category, null, 2)}
                </pre>
              )}
            </>
          )}

          {error && <p className="error">{error}</p>}
        </div>

        <div className="panel login">
          <div className="panelTitle">
            <ShieldCheck /> Secure access
          </div>
          <label>
            Government email
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          <button onClick={handleLogin} disabled={busy || !!token}>
            {token ? "Authenticated securely" : "Sign in"}
          </button>
          <small>
            MongoDB-backed platform. Default admin seeded on backend startup.
            Change credentials before public deployment.
          </small>
        </div>
      </section>

      <footer>
        <span>Suraksha Setu · Digital Public Safety Intelligence Platform</span>
        <span>Privacy by design · Explainable AI · Human oversight</span>
      </footer>
    </main>
  );
}
