# Smart Explainer App

Production-grade implementation of Smart Explainer - an AI-powered diagnostic platform using **Gemini 3** as a reasoning engine.

## Overview

Smart Explainer transforms raw technical inputs (errors, logs, stack traces, screenshots) into **structured, actionable explanations**.

This is **NOT a chatbot**. This is **AI-as-a-diagnostic-service**.

## Architecture

```
┌─────────────────┐
│   Next.js UI    │  ← Thin client (input collection + display)
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Spring Boot    │  ← Orchestration layer
│   REST API      │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────┐
│ Prompts │ │  Gemini  │  ← Reasoning engine
│ Service │ │  Client  │
└─────────┘ └────┬─────┘
                 │
                 ▼
         ┌───────────────┐
         │   Gemini 3    │
         │      API      │
         └───────────────┘
```

## Key Design Principles

1. **API-First**: Backend exposes clean REST APIs
2. **Prompts as Business Logic**: Externalized, versioned templates
3. **Gemini Isolation**: All AI calls through dedicated client
4. **Structured Output**: JSON schema validation enforced
5. **Separation of Concerns**: Frontend = UI, Backend = Orchestration, Gemini = Reasoning

## Tech Stack

### Backend
- Java 21
- Spring Boot 3
- WebClient (non-blocking HTTP)
- Maven

### Frontend
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- React 19

## Project Structure

```
smart-explainer-app/
├── backend/              # Spring Boot application
│   ├── src/main/java/com/smartexplainer/
│   │   ├── api/          # REST controllers
│   │   ├── service/      # Business logic
│   │   ├── ai/           # Gemini client
│   │   ├── model/        # DTOs
│   │   ├── config/       # Configuration
│   │   └── exception/    # Error handling
│   └── src/main/resources/
│       └── prompts/      # Externalized prompts
│
├── frontend/             # Next.js application
│   ├── app/              # Pages and layouts
│   ├── components/       # React components
│   ├── services/         # API client
│   └── types/            # TypeScript types
│
└── README.md
```

## Quick Start

### Prerequisites
- Java 21
- Node.js 18+
- Maven 3.8+
- Gemini API Key

### 1. Start Backend

```bash
cd backend

# Set your Gemini API key
export GEMINI_API_KEY=your-actual-api-key

# Run the application
mvn spring-boot:run
```

Backend runs on `http://localhost:8080`

### 2. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local with:
# NEXT_PUBLIC_API_URL=http://localhost:8080

# Run development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## API Endpoints

### Explain Text
```bash
POST http://localhost:8080/api/explain/text

{
  "content": "Exception in thread main java.lang.NullPointerException...",
  "context": "java"
}
```

### Explain Image
```bash
POST http://localhost:8080/api/explain/image

{
  "imageBase64": "<base64-encoded-image>",
  "context": "terminal-error"
}
```

### Response Format
```json
{
  "summary": "Brief issue summary",
  "rootCause": "Why this occurred",
  "diagnosticSteps": ["Step 1", "Step 2", "Step 3"],
  "suggestedFix": "How to resolve",
  "confidence": 0.88
}
```

## Why Gemini 3?

Smart Explainer relies on Gemini 3 for:

- **Deep reasoning** over technical text
- **Multimodal understanding** (screenshots, terminal output)
- **Low-latency inference** suitable for interactive workflows
- **Structured output control**, enabling API-first design

Without Gemini's reasoning capability, the system would degrade to static rule-based heuristics.

## Demo Flow (3 minutes)

1. **Text Analysis**:
   - Paste a Java NullPointerException
   - Show structured diagnosis with root cause and fix

2. **Image Analysis**:
   - Upload terminal error screenshot
   - Demonstrate multimodal reasoning

3. **Highlight**:
   - Structured JSON output
   - Confidence scoring
   - Gemini 3 reasoning in action

## What's Deliberately Excluded (MVP)

- Persistent storage
- User authentication
- Auto-remediation
- Streaming log ingestion

These are **future extensions**, not MVP goals.

## Documentation

See `docs/` folder for:
- API contract
- Design notes
- Architecture diagrams

## Guiding Principle

> **Gemini reasons.**  
> **Spring Boot orchestrates.**  
> **Clients consume structured intelligence.**

This principle drives all design decisions.
