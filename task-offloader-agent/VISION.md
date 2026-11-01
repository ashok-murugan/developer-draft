# TaskOffloaderAgent — Product Vision & Roadmap

> **For contributors:** This document is the authoritative product direction.
> Every architecture decision, feature, and milestone must be evaluated against this vision.

---

## 1. Core Product Vision

> **Use otherwise-unused local computing resources to reduce the computational and financial burden on cloud AI models, without compromising their reasoning capabilities, intelligence, or output quality.**

| Principle | Statement |
|---|---|
| **Cloud model is primary** | The cloud AI retains planning, reasoning, and all final decisions |
| **Local compute is optimization** | CPU, GPU, memory, and storage act as an acceleration and cost-reduction layer |
| **Never downgrade reasoning** | A weaker local model must never substitute for cloud reasoning on complex tasks |

---

## 2. What We Offload

### The distinction that drives every decision

A developer asks: *"Review my Spring Boot payment implementation for concurrency issues."*

A high-end cloud model is capable of reasoning about concurrency, transaction boundaries, and race conditions. **We do not replace that reasoning.** We reduce the work the cloud model must perform *before* it reasons.

```
┌────────────────────────────────┐     ┌──────────────────────────────────┐
│   Cloud Model (Preserved)      │     │   Local Compute (Offloaded)       │
│                                │     │                                   │
│ • Understand business context  │     │ • Parse source code               │
│ • Reason about concurrency     │     │ • Build AST and dependency index  │
│ • Identify subtle bugs         │     │ • Identify relevant files         │
│ • Design solutions             │     │ • Extract methods and symbols     │
│ • Evaluate trade-offs          │     │ • Analyze Git changes             │
│ • Generate implementation      │     │ • Search logs and documentation   │
│                                │     │ • Calculate dependency impact     │
│                                │     │ • Deduplicate and compress        │
│                                │     │ • Cache reusable results          │
└────────────────────────────────┘     └──────────────────────────────────┘
           ▲                                          │
           └──────── Relevant, compact evidence ──────┘
```

> [!IMPORTANT]
> We transfer **supporting computation** to local resources.
> We never transfer **difficult reasoning** to a weaker model.

---

## 3. Three Optimization Strategies

### A. Computational Offloading — Highest Priority

Move deterministic work to local hardware. No LLM required.

| Workload | Local execution |
|---|---|
| AST parsing | CPU |
| Symbol indexing | CPU |
| Dependency analysis | CPU |
| Git diff analysis | CPU |
| Log filtering | CPU |
| File hashing + deduplication | CPU |
| Context ranking | CPU |
| Repeated result caching | CPU + disk |
| Optional summarization | GPU/CPU via Ollama |

> [!TIP]
> The biggest opportunity is **deterministic computation**. You don't need a GPU or LLM to find all callers of a Java method.

### B. Context Optimization — Highest Priority

Reduce unnecessary tokens sent to cloud models.

| Approach | Approximate input tokens |
|---|---|
| Entire repository context | 100,000 |
| Basic file filtering | 35,000 |
| AST + dependency analysis | 12,000 |
| Evidence-based context retrieval | 5,000 |

> *Illustrative example — not measured benchmarks.*

The cloud model still receives all the information needed to reason correctly. It just receives **less noise**.

### C. Local Inference Offloading — Selective Priority

Use Ollama only for tasks where a local model is **sufficiently capable**:

- Log summarization
- Simple document extraction
- Classification
- Formatting
- Basic metadata extraction

> [!WARNING]
> Local inference is **not** the primary optimization strategy.
> A local LLM consumes RAM, GPU memory, and electricity and adds latency.
> Sometimes deterministic CPU processing is cheaper, faster, and more reliable.

---

## 4. Target Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│              Primary Cloud AI Agent                             │
│         GPT · Claude · Gemini · Cursor                          │
│   Retains planning, reasoning, and all final decisions          │
│   Delegates supporting work through MCP (stdio)                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ MCP
┌──────────────────────▼──────────────────────────────────────────┐
│                  TaskOffloaderAgent                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. Compute Optimization Engine                          │   │
│  │    Task decomposition · Resource-aware scheduling        │   │
│  │    Offloading decisions · Budget management              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────┐  ┌───────────────────┐                   │
│  │ 2. Code          │  │ 3. Context Engine  │                   │
│  │    Intelligence  │  │    Retrieval       │                   │
│  │    AST · Graph   │  │    Ranking         │                   │
│  │    Dependencies  │  │    Caching         │                   │
│  └──────────────────┘  └───────────────────┘                   │
│                                                                 │
│  ┌──────────────────┐  ┌───────────────────┐                   │
│  │ 4. Deterministic │  │ 5. Local Inference │                   │
│  │    Workers       │  │    Ollama          │                   │
│  │    Parsing       │  │    Optional models │                   │
│  │    Filtering     │  │    Selective only  │                   │
│  └──────────────────┘  └───────────────────┘                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 6. Shared Foundation                                    │   │
│  │    Security · Audit · Token budgets · Observability     │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Optimized evidence
┌──────────────────────▼──────────────────────────────────────────┐
│   Cloud model receives compact, verified, ranked evidence       │
│   and performs the actual reasoning                             │
└─────────────────────────────────────────────────────────────────┘
```

> [!IMPORTANT]
> TaskOffloaderAgent must **never silently take over** the cloud model's reasoning responsibilities.
> It provides evidence, computation, and reusable results.
> The primary agent decides how to use them.

---

## 5. Implementation Milestones

### M0 — Establish the Optimization Baseline

> *Before building new capabilities, measure where cloud-model expenditure actually occurs.*

- [ ] Record input/output tokens per task type
- [ ] Identify repeated context and redundant file reads
- [ ] Measure local CPU, memory, and GPU availability
- [ ] Establish task-quality baselines
- [ ] Define cloud cost per task type

**Deliverable:** Optimization benchmark + architecture decision record  
**Exit gate:** We know which workloads are worth offloading and their relative cost

---

### M1 — Local Compute Optimization Engine

> *Build the foundation for utilizing idle resources.*

- [ ] Resource detection (CPU, memory, GPU, battery state)
- [ ] Resource-aware scheduling (idle vs. loaded vs. battery policies)
- [ ] Deterministic task execution with safe cancellation
- [ ] Background indexing without blocking the developer workflow
- [ ] Task prioritization and concurrency limits
- [ ] Timeouts and resource caps

**Deliverable:** Local compute scheduler  
**Exit gate:** Tasks execute locally without affecting the primary developer workflow

---

### M2 — Deterministic Intelligence

- [ ] Tree-sitter AST parsing
- [ ] Symbol indexing (methods, classes, interfaces)
- [ ] Dependency extraction and call graph
- [ ] Git change analysis (diff, blame, history)
- [ ] Incremental indexing (only re-index changed files)
- [ ] SQLite persistence for reusable indexes

**Deliverable:** Local code-intelligence engine  
**Exit gate:** Repository structural understanding no longer requires an LLM

---

### M3 — Provider Adapter Framework

- [ ] Native intelligence provider (built-in deterministic)
- [ ] CRG adapter
- [ ] Graphify adapter
- [ ] Capability discovery (what each provider can answer)
- [ ] Provider health and index freshness checks
- [ ] Normalized evidence contracts (same shape regardless of provider)

**Deliverable:** Interchangeable intelligence providers  
**Exit gate:** Provider choice does not change the application's core behaviour

---

### M4 — Context Optimization Engine

- [ ] Evidence-based retrieval (fetch only what is relevant)
- [ ] Context ranking (most relevant evidence ranked first)
- [ ] Token-aware packaging (fit within cloud model's budget)
- [ ] Deduplication of evidence across files and calls
- [ ] Local caching of ranked contexts
- [ ] Citation validation (every reference is verified)
- [ ] Missing-context detection (flag gaps before sending to cloud)

**Deliverable:** Cloud-ready optimized context  
**Exit gate:** Measurable reduction in cloud input tokens with no material quality loss

---

### M5 — Adaptive Offloading and Optimization

- [ ] Task classification (what is safe to offload vs. must stay in cloud)
- [ ] Resource-aware routing (CPU/GPU/Ollama/cloud decision)
- [ ] Optional local inference via Ollama (classification, summaries, formatting)
- [ ] Cost estimation before execution (is local actually cheaper?)
- [ ] Cloud/local execution policies (configurable per workspace)
- [ ] Performance monitoring and regression alerts
- [ ] Quality regression testing (non-inferiority evaluation)

**Deliverable:** Intelligent local-first optimization workflow  
**Exit gate:** Demonstrate measurable savings while preserving cloud model reasoning capability

---

## 6. Resource Policy

> [!CAUTION]
> **Unused computing does not automatically mean free computing.**
> Ollama running continuously can consume significant RAM, GPU memory, electricity, and CPU.
> The scheduler must consider the actual end-to-end benefit — not just whether local execution is *possible*.

| Machine state | Agent behaviour |
|---|---|
| Machine idle | Allow background indexing |
| Lightly loaded | Execute low-priority tasks |
| Under heavy load | Defer optional tasks |
| Low available memory | Avoid local inference |
| Developer actively compiling | Prioritise interactive workflow |
| Laptop on battery | Restrict expensive background work |
| Cloud task needs immediate response | Do not delay for local processing |

---

## 7. How We Prove Cloud Performance Is Unaffected

This is the **central success criterion** — not capability count.

### Three comparison modes

| Experiment | Setup |
|---|---|
| **A — Cloud baseline** | Original prompt, normal workflow, no local optimization |
| **B — Cloud + deterministic local** | Same cloud model; local analysis prepares evidence |
| **C — Cloud + deterministic + local inference** | Same cloud model; suitable supporting tasks via Ollama |

### Measurement matrix

| Metric | Required outcome |
|---|---|
| Cloud model version | Identical across A/B/C |
| Answer correctness | Non-inferior (within ε margin) |
| Reasoning capability | Preserved |
| Cloud input tokens | Reduced |
| Total cloud cost | Reduced |
| End-to-end latency | No unacceptable regression |
| Local resource usage | Controlled by resource policy |
| Missing evidence | Minimal |
| Security violations | Zero |

> [!NOTE]
> Use **non-inferiority evaluation**, not equivalence testing.
> Different context packaging changes outputs even when the model is identical.
> Initial target: ≥ 50% median input-token reduction on suitable tasks with no material correctness decline.

---

## 8. Success Definition (KPIs)

The product is measured by **cloud work eliminated without sacrificing quality** — not by feature count.

### Net savings formula

$$
\text{Net Savings} = \text{Baseline Cloud Cost} - \text{Optimized Cloud Cost} - \text{Incremental Local Cost}
$$

Where **incremental local cost** includes electricity, additional hardware usage, and operational overhead.

### Quality constraint

$$
Q_{\text{optimized}} \geq Q_{\text{baseline}} - \varepsilon
$$

Where **ε** is a small, predefined non-inferiority margin set per benchmark task.

---

## 9. One-Line Positioning (for contributors)

> **TaskOffloaderAgent is a local compute and context optimization layer for cloud AI — not a local AI development agent.**

Every PR, feature, and design decision should be evaluated against this sentence.

---

*Last updated: 2026-11-01*
