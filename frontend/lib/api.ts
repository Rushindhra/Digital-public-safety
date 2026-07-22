const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export type TokenPair = { access_token: string; refresh_token: string };

export async function login(email: string, password: string): Promise<TokenPair> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
  return res.json();
}

export async function apiFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function analyseScam(token: string, content: string) {
  return apiFetch(`${"/scam/analyse"}`, token, {
    method: "POST",
    body: JSON.stringify({ content, channel: "chat", language: "en" }),
  });
}

export async function fetchReports(token: string) {
  return apiFetch("/reports", token);
}

export async function fetchAnalytics(token: string) {
  return apiFetch("/analytics/summary", token);
}

export async function fetchHotspots(token: string) {
  return apiFetch("/geo/hotspots", token);
}

export async function analyseGraph(token: string, nodes: object[], edges: object[]) {
  return apiFetch("/graph/analyse", token, {
    method: "POST",
    body: JSON.stringify({ nodes, edges }),
  });
}

export async function chatAssistant(token: string, message: string) {
  return apiFetch("/assistant/chat", token, {
    method: "POST",
    body: JSON.stringify({ message, language: "en" }),
  });
}

export async function createReport(
  token: string,
  report: {
    category: string;
    title: string;
    description: string;
    district?: string;
    risk_score?: number;
  }
) {
  return apiFetch("/reports", token, {
    method: "POST",
    body: JSON.stringify({ ...report, channel: "web" }),
  });
}

export async function analyseCounterfeit(
  token: string,
  file: File,
  denomination: number
) {
  const form = new FormData();
  form.append("image", file);
  const res = await fetch(
    `${API_BASE}/counterfeit/analyse?denomination=${denomination}`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: form,
    }
  );
  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}
