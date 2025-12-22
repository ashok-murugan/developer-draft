# Sequence Diagram

## Request Flow: Text Explanation

```
┌────────┐         ┌──────────┐         ┌─────────────┐         ┌──────────┐         ┌─────────┐
│ Client │         │   API    │         │  Diagnostic │         │  Prompt  │         │ Gemini  │
│        │         │Controller│         │   Service   │         │ Service  │         │ Client  │
└───┬────┘         └────┬─────┘         └──────┬──────┘         └────┬─────┘         └────┬────┘
    │                   │                       │                     │                    │
    │  POST /explain/text                       │                     │                    │
    │  {content, context}                       │                     │                    │
    ├──────────────────►│                       │                     │                    │
    │                   │                       │                     │                    │
    │                   │  Validate request     │                     │                    │
    │                   │  ────────────         │                     │                    │
    │                   │             │         │                     │                    │
    │                   │  ◄───────────         │                     │                    │
    │                   │                       │                     │                    │
    │                   │  explainText(content, context)              │                    │
    │                   ├──────────────────────►│                     │                    │
    │                   │                       │                     │                    │
    │                   │                       │  buildDiagnosticPrompt(content, context) │
    │                   │                       ├────────────────────►│                    │
    │                   │                       │                     │                    │
    │                   │                       │  Load template      │                    │
    │                   │                       │  Replace placeholders                    │
    │                   │                       │  ──────────────     │                    │
    │                   │                       │               │     │                    │
    │                   │                       │  ◄─────────────     │                    │
    │                   │                       │                     │                    │
    │                   │                       │  Prompt string      │                    │
    │                   │                       │◄────────────────────┤                    │
    │                   │                       │                     │                    │
    │                   │                       │  generateContent(prompt)                 │
    │                   │                       ├─────────────────────────────────────────►│
    │                   │                       │                     │                    │
    │                   │                       │                     │  Build request     │
    │                   │                       │                     │  Call Gemini API   │
    │                   │                       │                     │  ──────────────    │
    │                   │                       │                     │               │    │
    │                   │                       │                     │  ◄─────────────    │
    │                   │                       │                     │                    │
    │                   │                       │                     │                    │
    │                   │                       │                     │   ┌──────────────┐ │
    │                   │                       │                     │   │  Gemini 3    │ │
    │                   │                       │                     │   │     API      │ │
    │                   │                       │                     │   └──────┬───────┘ │
    │                   │                       │                     │          │         │
    │                   │                       │                     │   Reasoning        │
    │                   │                       │                     │   Analysis         │
    │                   │                       │                     │   ──────────       │
    │                   │                       │                     │          │         │
    │                   │                       │                     │   ◄───────         │
    │                   │                       │                     │                    │
    │                   │                       │  JSON response      │                    │
    │                   │                       │◄─────────────────────────────────────────┤
    │                   │                       │                     │                    │
    │                   │                       │  Parse & validate   │                    │
    │                   │                       │  ──────────────     │                    │
    │                   │                       │               │     │                    │
    │                   │                       │  ◄─────────────     │                    │
    │                   │                       │                     │                    │
    │                   │  DiagnosticResponse   │                     │                    │
    │                   │◄──────────────────────┤                     │                    │
    │                   │                       │                     │                    │
    │  200 OK           │                       │                     │                    │
    │  {                │                       │                     │                    │
    │    summary,       │                       │                     │                    │
    │    rootCause,     │                       │                     │                    │
    │    diagnosticSteps,                       │                     │                    │
    │    suggestedFix,  │                       │                     │                    │
    │    confidence     │                       │                     │                    │
    │  }                │                       │                     │                    │
    │◄──────────────────┤                       │                     │                    │
    │                   │                       │                     │                    │
```

## Request Flow: Image Explanation

```
┌────────┐         ┌──────────┐         ┌─────────────┐         ┌──────────┐         ┌─────────┐
│ Client │         │   API    │         │  Diagnostic │         │  Prompt  │         │ Gemini  │
│        │         │Controller│         │   Service   │         │ Service  │         │ Client  │
└───┬────┘         └────┬─────┘         └──────┬──────┘         └────┬─────┘         └────┬────┘
    │                   │                       │                     │                    │
    │  POST /explain/image                      │                     │                    │
    │  {imageBase64, context}                   │                     │                    │
    ├──────────────────►│                       │                     │                    │
    │                   │                       │                     │                    │
    │                   │  Validate request     │                     │                    │
    │                   │  ────────────         │                     │                    │
    │                   │             │         │                     │                    │
    │                   │  ◄───────────         │                     │                    │
    │                   │                       │                     │                    │
    │                   │  explainImage(base64, context)              │                    │
    │                   ├──────────────────────►│                     │                    │
    │                   │                       │                     │                    │
    │                   │                       │  buildDiagnosticPrompt(text, context)    │
    │                   │                       ├────────────────────►│                    │
    │                   │                       │                     │                    │
    │                   │                       │  Prompt string      │                    │
    │                   │                       │◄────────────────────┤                    │
    │                   │                       │                     │                    │
    │                   │                       │  generateContentWithImage(prompt, base64)│
    │                   │                       ├─────────────────────────────────────────►│
    │                   │                       │                     │                    │
    │                   │                       │                     │  Build multimodal  │
    │                   │                       │                     │  request (text +   │
    │                   │                       │                     │  image parts)      │
    │                   │                       │                     │  ──────────────    │
    │                   │                       │                     │               │    │
    │                   │                       │                     │  ◄─────────────    │
    │                   │                       │                     │                    │
    │                   │                       │                     │   ┌──────────────┐ │
    │                   │                       │                     │   │  Gemini 3    │ │
    │                   │                       │                     │   │     API      │ │
    │                   │                       │                     │   │ (Multimodal) │ │
    │                   │                       │                     │   └──────┬───────┘ │
    │                   │                       │                     │          │         │
    │                   │                       │                     │   Image analysis   │
    │                   │                       │                     │   Text reasoning   │
    │                   │                       │                     │   ──────────       │
    │                   │                       │                     │          │         │
    │                   │                       │                     │   ◄───────         │
    │                   │                       │                     │                    │
    │                   │                       │  JSON response      │                    │
    │                   │                       │◄─────────────────────────────────────────┤
    │                   │                       │                     │                    │
    │                   │  DiagnosticResponse   │                     │                    │
    │                   │◄──────────────────────┤                     │                    │
    │                   │                       │                     │                    │
    │  200 OK           │                       │                     │                    │
    │  {structured JSON}│                       │                     │                    │
    │◄──────────────────┤                       │                     │                    │
    │                   │                       │                     │                    │
```

## Error Flow

```
┌────────┐         ┌──────────┐         ┌─────────────┐         ┌─────────┐
│ Client │         │   API    │         │  Diagnostic │         │ Gemini  │
│        │         │Controller│         │   Service   │         │ Client  │
└───┬────┘         └────┬─────┘         └──────┬──────┘         └────┬────┘
    │                   │                       │                     │
    │  Invalid request  │                       │                     │
    ├──────────────────►│                       │                     │
    │                   │                       │                     │
    │                   │  Validation fails     │                     │
    │                   │  ────────────         │                     │
    │                   │             │         │                     │
    │                   │  ◄───────────         │                     │
    │                   │                       │                     │
    │  400 Bad Request  │                       │                     │
    │  {                │                       │                     │
    │    errorCode: "INVALID_INPUT",            │                     │
    │    message: "..."│                       │                     │
    │  }                │                       │                     │
    │◄──────────────────┤                       │                     │
    │                   │                       │                     │
    │                   │                       │                     │
    │  Valid request    │                       │                     │
    ├──────────────────►│                       │                     │
    │                   ├──────────────────────►│                     │
    │                   │                       ├────────────────────►│
    │                   │                       │                     │
    │                   │                       │                     │  Gemini API error
    │                   │                       │                     │  ──────────────
    │                   │                       │                     │               │
    │                   │                       │                     │  ◄─────────────
    │                   │                       │                     │
    │                   │                       │  GeminiClientException
    │                   │                       │◄────────────────────┤
    │                   │                       │                     │
    │                   │  Exception propagated │                     │
    │                   │◄──────────────────────┤                     │
    │                   │                       │                     │
    │  500 Internal Error                       │                     │
    │  {                │                       │                     │
    │    errorCode: "GEMINI_ERROR",             │                     │
    │    message: "..." │                       │                     │
    │  }                │                       │                     │
    │◄──────────────────┤                       │                     │
    │                   │                       │                     │
```

## Key Observations

1. **Clean Separation**: Each component has a single responsibility
2. **Prompt Externalization**: Templates loaded and populated at runtime
3. **Gemini Isolation**: All AI calls go through dedicated client
4. **Error Handling**: Consistent error responses at each layer
5. **Multimodal Support**: Same flow for text and image, different Gemini call
6. **Validation**: Input validated before processing
7. **Structured Output**: Response always follows schema
