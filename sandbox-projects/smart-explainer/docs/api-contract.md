# API Contract — Smart Explainer

This document defines the **public API contracts** exposed by the Smart Explainer backend.

The API is **API-first and machine-consumable**.

---

## Base URL

```
/api/explain
```

---

## 1️⃣ Explain Text

### Endpoint

```
POST /api/explain/text
```

### Request Body
```json
{
  "content": "Exception in thread main java.lang.NullPointerException ...",
  "context": "java"
}
```

### Response Body
```json
{
  "summary": "NullPointerException at Service.process line 42.",
  "rootCause": "A variable was accessed before being initialized.",
  "diagnosticSteps": [
    "Inspect Service.process at line 42",
    "Run application with debugger or add logging"
  ],
  "suggestedFix": "Add null checks or ensure proper initialization.",
  "confidence": 0.88
}
```

---

## 2️⃣ Explain Image

### Endpoint

```
POST /api/explain/image
```

### Request Body
```json
{
  "imageBase64": "<base64-encoded-image>",
  "context": "terminal-error"
}
```

### Response Body

(Same schema as text explanation)

```json
{
  "summary": "NullPointerException at Service.process line 42.",
  "rootCause": "A variable was accessed before being initialized.",
  "diagnosticSteps": [
    "Inspect Service.process at line 42",
    "Run application with debugger or add logging"
  ],
  "suggestedFix": "Add null checks or ensure proper initialization.",
  "confidence": 0.88
}
```

---

## ⚠️ Error Response

```json
{
  "errorCode": "INVALID_INPUT",
  "message": "Input content is empty or unreadable"
}
```
