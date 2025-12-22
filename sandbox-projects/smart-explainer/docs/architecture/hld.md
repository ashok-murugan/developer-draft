# Architecture Diagrams

## High-Level Design (HLD)

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  UI / CLI / CI Tools / External Systems          │   │
│  │  (Next.js, curl, scripts, etc.)                  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ HTTP Request
                         │ (JSON payload)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   API LAYER                              │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Spring Boot REST API                     │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │  POST /api/explain/text                    │  │   │
│  │  │  POST /api/explain/image                   │  │   │
│  │  │  GET  /api/explain/health                  │  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ Orchestration
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 SERVICE LAYER                            │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │   Prompt Service     │  │  Diagnostic Service      │ │
│  │                      │  │                          │ │
│  │  • Load templates    │  │  • Coordinate flow       │ │
│  │  • Build prompts     │  │  • Validate responses    │ │
│  │  • Version control   │  │  • Error handling        │ │
│  └──────────────────────┘  └──────────────────────────┘ │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ AI Request
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   AI LAYER                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Gemini Client                         │   │
│  │                                                  │   │
│  │  • Isolated integration                          │   │
│  │  • Retry logic                                   │   │
│  │  • Timeout handling                              │   │
│  │  • Response parsing                              │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ WebClient (non-blocking)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                 GEMINI 3 API                             │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Reasoning Engine                         │   │
│  │                                                  │   │
│  │  • Deep technical reasoning                      │   │
│  │  • Multimodal understanding                      │   │
│  │  • Structured output generation                  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ Structured JSON Response
                         ▼
                    ┌─────────┐
                    │ Client  │
                    └─────────┘
```

## Key Components

### 1. Client Layer
- **Purpose**: Input collection and result presentation
- **Examples**: Next.js UI, CLI tools, CI/CD integrations
- **Responsibility**: User interaction only

### 2. API Layer (Spring Boot)
- **Purpose**: REST API contract enforcement
- **Endpoints**: `/text`, `/image`, `/health`
- **Responsibility**: Request validation, response formatting

### 3. Service Layer
- **Prompt Service**: Manages externalized prompt templates
- **Diagnostic Service**: Orchestrates the diagnostic flow
- **Responsibility**: Business logic coordination

### 4. AI Layer (Gemini Client)
- **Purpose**: Isolated Gemini integration
- **Features**: Retry, timeout, error handling
- **Responsibility**: AI communication abstraction

### 5. Gemini 3 API
- **Purpose**: Core reasoning engine
- **Capabilities**: Text + image understanding
- **Responsibility**: Generate structured diagnostics

## Data Flow

1. Client sends error/image to API
2. API validates and routes to DiagnosticService
3. DiagnosticService builds prompt via PromptService
4. GeminiClient calls Gemini 3 API
5. Response parsed and validated
6. Structured JSON returned to client

## Design Principles

- **Separation of Concerns**: Each layer has single responsibility
- **Gemini Isolation**: AI logic contained in dedicated client
- **Prompts as Code**: Templates externalized and versioned
- **API-First**: Backend reusable by any client
