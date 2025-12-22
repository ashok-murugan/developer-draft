# Smart Explainer

Smart Explainer is an **AI-powered diagnostic service** that uses **Gemini 3 as a reasoning engine**
to transform raw technical inputs (errors, logs, stack traces, screenshots) into
**structured, actionable explanations**.

This project is built in two phases:
1. **MVP (AI Studio Prototype)** — validates Gemini reasoning and multimodal capability
2. **Engineering Edition (Spring Boot + Next.js)** — production-shaped backend API with clean architecture

---

## 🎯 Problem

Engineers spend significant time manually interpreting:
- Stack traces and error logs
- CLI and runtime errors
- Screenshots of failures or misconfigurations

Existing tools surface data, but **do not reason** about:
- Why an issue occurred
- What to check first
- What actions are most likely to fix it

---

## 💡 Solution

Smart Explainer introduces **AI-driven reasoning** into diagnostics.

It:
- Accepts text or image-based technical input
- Uses Gemini 3 to reason step-by-step
- Returns a **machine-consumable JSON diagnosis** containing:
  - Summary
  - Root cause
  - Diagnostic steps
  - Suggested fix
  - Confidence score

Gemini is not a chatbot here — it is the **core reasoning layer**.

---

## 🧠 Why Gemini 3?

Smart Explainer relies on Gemini 3 for:
- **Deep reasoning** over technical text
- **Multimodal understanding** (screenshots, terminal output)
- **Low-latency inference** suitable for interactive workflows
- **Structured output control**, enabling API-first design

Without Gemini’s reasoning capability, the system would degrade to static rule-based heuristics.

---

## 🏗️ Architecture Overview

At a high level:

Client (UI / Tool)
↓
Spring Boot API
↓
Prompt Orchestration
↓
Gemini 3 API
↓
Structured Diagnostic Output


- Prompts are treated as **versioned business logic**
- Gemini integration is isolated behind a client abstraction
- Outputs are normalized and validated before returning to clients

See detailed diagrams in `docs/architecture/`.

---

## 📂 Repository Structure



smart-explainer/
├── mvp/ # AI Studio prototype
├── smart-explainer-app/ # Production-grade implementation
├── docs/ # Architecture & design documentation
└── README.md