# Digital Public Safety Intelligence Platform — Architecture

## 1. Scope Decision (read this first)

This platform is being built incrementally, module by module, with real working
code at each step. Some AI components use genuinely trained/fine-tuned models;
others use well-justified classical ML or rule-based systems where that's the
honest, correct engineering choice (e.g., no labeled counterfeit-note dataset
exists publicly at scale, so that module uses supervised feature-based
detection on synthetic + augmented data, not a black-box "it's AI" claim).
Every module's README will state plainly what's real, what's a heuristic, and
what would need real government data access to become production-grade.

## 2. High-Level Architecture

```
                                   ┌─────────────────────────┐
                                   │   Citizens / Officers    │
                                   │  (Web, Mobile, WhatsApp) │
                                   └────────────┬─────────────┘
                                                │ HTTPS/WSS
                                   ┌────────────▼─────────────┐
                                   │      Next.js Frontend     │
                                   │  (Citizen Portal + LE     │
                                   │   Dashboard, RBAC-aware)  │
                                   └────────────┬─────────────┘
                                                │ REST + WebSocket
                                   ┌────────────▼─────────────┐
                                   │     FastAPI Gateway       │
                                   │  Auth · Rate Limit · CORS │
                                   └───┬───────┬───────┬──────┘
                    ┌──────────────────┘       │       └──────────────────┐
         ┌──────────▼─────────┐   ┌────────────▼───────────┐   ┌──────────▼─────────┐
         │  Core Domain API   │   │     AI Service Layer     │   │   Realtime/Notify   │
         │ (cases, reports,   │   │  (scam NLP, CV, graph,   │   │  (WS, Celery+Redis, │
         │  users, evidence)  │   │   RAG agents, geospatial)│   │   SMS/email sim)    │
         └──────────┬─────────┘   └────────────┬───────────┘   └──────────┬─────────┘
                    │                          │                          │
         ┌──────────▼───────────────────────────▼──────────────────────────▼─────────┐
         │                          Data Layer                                        │
         │  PostgreSQL (relational) · Redis (cache/queue) · Qdrant (vectors)          │
         │  Object storage (evidence files, note images)                              │
         └──────────────────────────────────────────────────────────────────────────┘
```

## 3. Tech Stack — Decisions & Trade-offs

| Layer | Choice | Why | Alternative considered |
|---|---|---|---|
| Frontend | Next.js 14 (App Router) + TS + Tailwind + shadcn/ui | SSR for dashboards, great DX, accessible components out of box | Vite+React SPA — rejected: no SSR, worse SEO for public citizen portal |
| Backend | FastAPI | Async native, auto OpenAPI docs, first-class Pydantic validation, easy ML integration | Django — rejected: heavier, async story weaker for ML inference |
| DB | PostgreSQL | ACID, JSONB for flexible evidence metadata, PostGIS for geospatial | MongoDB — rejected: we need real relational integrity for fraud graphs/cases |
| Cache/Queue | Redis + Celery | Battle-tested, simple ops story for background jobs (report processing, notifications) | RabbitMQ — more powerful but overkill at this stage |
| Vector DB | Qdrant | Self-hostable, fast, simple REST/gRPC API, good filtering for RAG | Pinecone — rejected: not self-hostable, cost at scale |
| Graph analysis | NetworkX (+ optional PyG later) | Pure Python, no GPU needed, sufficient for fraud-ring detection at MVP scale | Neo4j — better at scale, deferred until real transaction volume justifies it |
| CV (counterfeit) | OpenCV feature engineering + scikit-learn classifier (extensible to CNN) | Explainable (regulators/courts need explainability), works without huge labeled datasets | End-to-end CNN — planned as v2 once a labeled note dataset is sourced |
| NLP (scam detection) | Sentence-Transformers embeddings + classifier, rules for impersonation patterns | Fast, interpretable, works multilingual with multilingual-MiniLM | Fine-tuned LLM — deferred: cost/latency not justified at MVP |
| Auth | JWT (access + refresh) via FastAPI + passlib | Standard, stateless, scales horizontally | Session-based — rejected: worse for multi-service scaling |

## 4. Module Build Order (this session onward)

1. Core backend skeleton + auth + DB models — **complete**
2. Counterfeit Currency Detection (CV) — **screening pipeline complete**
3. Digital Arrest Scam Detection (NLP) — real embedding classifier + rule engine — **next**
4. Fraud Network Intelligence (Graph) — real NetworkX pipeline
5. Geospatial Intelligence — real heatmap/hotspot clustering (DBSCAN)
6. Citizen Fraud Shield — RAG chat agent tying it together
7. Law Enforcement Dashboard — frontend wiring all of the above

## 5. Non-Goals for MVP (documented, not hidden)

- No real government data integration (NCRB/RBI/CERT-In APIs don't exist
  publicly) — RAG knowledge base uses public advisories we can legitimately
  fetch/cite.
- No production SMS/WhatsApp sending — simulated via a mock provider interface
  swappable for Twilio/Gupshup later.
- No GPU-trained deep CV model in MVP — architecture supports swapping the
  classifier for a CNN without touching the API contract.
