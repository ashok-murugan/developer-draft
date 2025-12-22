# Design Notes — Smart Explainer

This document captures **key architectural and design decisions**.

---

## 1️⃣ Why API-First?

Smart Explainer is designed as a **backend diagnostic platform**, not a UI-driven chatbot.

Benefits:
- Reusable by multiple clients (UI, CLI, CI tools)
- Easier integration into existing workflows
- Clear separation of concerns

---

## 2️⃣ Prompts as Business Logic

Instead of hardcoding logic in Java:
- Prompt templates define reasoning steps
- Prompts are versioned and externalized
- Changes in reasoning do not require recompilation

This aligns with modern AI-native system design.

---

## 3️⃣ Gemini Isolation

Gemini integration is encapsulated in a dedicated client layer.

Reasons:
- Avoid AI leakage across services
- Enable future model/version replacement
- Centralize retry, timeout, and error handling

---

## 4️⃣ Structured Output Enforcement

All Gemini outputs are:
- Parsed
- Normalized
- Validated against a schema

This ensures:
- Predictable API responses
- Safe consumption by downstream systems
- Reduced hallucination impact

---

## 5️⃣ What We Deliberately Avoided

For initial versions:
- Persistent storage
- User authentication
- Auto-remediation
- Streaming log ingestion

These are **future extensions**, not MVP goals.

---

## 6️⃣ Guiding Principle

> Gemini reasons.  
> Spring Boot orchestrates.  
> Clients consume structured intelligence.

This principle drives all design decisions.
