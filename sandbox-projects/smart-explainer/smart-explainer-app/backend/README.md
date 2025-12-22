# Smart Explainer Backend

Production-grade Spring Boot backend for the Smart Explainer diagnostic platform.

## Architecture

```
Client Request
    ↓
ExplainController (API Layer)
    ↓
DiagnosticService (Orchestration)
    ↓
PromptService (Business Logic) + GeminiClient (AI Layer)
    ↓
Gemini 3 API
    ↓
Structured JSON Response
```

## Key Design Principles

1. **API-First**: Clean REST API contract
2. **Prompts as Business Logic**: Externalized in `resources/prompts/`
3. **Gemini Isolation**: All AI calls through `GeminiClient`
4. **Structured Output**: JSON schema validation enforced

## Prerequisites

- Java 21
- Maven 3.8+
- Gemini API Key

## Setup

1. **Set your Gemini API key**:
   ```bash
   export GEMINI_API_KEY=your-actual-api-key
   ```

2. **Build the project**:
   ```bash
   mvn clean install
   ```

3. **Run the application**:
   ```bash
   mvn spring-boot:run
   ```

The server will start on `http://localhost:8080`

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

### Health Check
```bash
GET http://localhost:8080/api/explain/health
```

## Response Format

All diagnostic endpoints return:

```json
{
  "summary": "Brief issue summary",
  "rootCause": "Why this occurred",
  "diagnosticSteps": ["Step 1", "Step 2", "Step 3"],
  "suggestedFix": "How to resolve",
  "confidence": 0.88
}
```

## Project Structure

```
src/main/java/com/smartexplainer/
├── api/                    # REST controllers
├── service/                # Business logic orchestration
├── ai/                     # Gemini client isolation
├── model/                  # Request/response DTOs
├── config/                 # Spring configuration
└── exception/              # Error handling

src/main/resources/
└── prompts/                # Externalized prompt templates
```

## Testing

Run tests with:
```bash
mvn test
```

## Environment Variables

- `GEMINI_API_KEY`: Your Gemini API key (required)
- `SERVER_PORT`: Server port (default: 8080)

## Notes

- No database or persistence layer in MVP
- No authentication/authorization in MVP
- Prompts are versioned and externalized
- All Gemini responses are validated against schema
