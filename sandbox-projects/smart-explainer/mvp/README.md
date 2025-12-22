# Smart Explainer — MVP

> **Gemini-powered error and screenshot explainer with structured output**

An AI-powered tool that helps engineers quickly understand and resolve technical errors, log messages, and system issues. Built with Google AI Studio and Gemini 3, Smart Explainer provides instant, actionable explanations in both human-readable and structured JSON formats.

## 🎯 What It Does

Smart Explainer analyzes:
- **Error messages** (stack traces, exceptions, build failures)
- **Log excerpts** (application logs, system logs)
- **Screenshots** (terminal errors, code screenshots, whiteboard diagrams)
- **Technical descriptions** (performance issues, system behavior)

And provides:
1. **One-line summary** of what's happening
2. **Root cause analysis** with 2-3 most likely causes
3. **Diagnostic steps** with exact commands to run
4. **Suggested fixes** with code snippets or commands
5. **Confidence score** with reasoning

## 🚀 Try It Now

**Live Demo**: [AI Studio App Link - Coming Soon]

*(Link will be added after publishing to AI Studio)*

## ✨ Key Features

### 🔤 Text Mode
Paste any error message, log excerpt, or technical description and get instant analysis.

### 🖼️ Image Mode
Upload screenshots of terminal errors, stack traces, or whiteboard diagrams for visual analysis.

### 📊 JSON Output
Toggle structured JSON output for programmatic consumption and integration with other tools.

### 💡 Example Inputs
Pre-loaded examples to test the system:
- Java NullPointerException
- Port binding errors
- Microservice latency issues

## 🏗️ Project Structure

```
mvp-ai-studio/
├── README.md                          # This file
├── prompts/                           # AI prompts for different modes
│   ├── explain-text.prompt.md        # Human-friendly text explanations
│   ├── explain-image.prompt.md       # Image analysis with vision
│   └── explain-json.prompt.md        # Structured JSON output
├── samples/                           # Test inputs
│   ├── text-inputs/                  # Sample error messages
│   │   ├── java-nullpointer.txt
│   │   ├── port-in-use.txt
│   │   └── microservice-latency.txt
│   └── image-inputs/                 # Sample screenshots
│       ├── stacktrace-screenshot.png
│       ├── terminal-error.png
│       └── whiteboard-diagram.jpg
├── outputs/                           # Example outputs
│   ├── sample-human-readable.md      # Human-friendly format
│   └── sample-structured-output.json # JSON format
├── demo/                              # Demo materials
│   ├── demo-script.md                # Recording script
│   ├── test-results.csv              # Testing documentation
│   └── screenshots/                  # UI screenshots
└── ai-studio/                         # AI Studio configuration
    ├── app-config.md                 # Setup instructions
    └── public-link.txt               # Published app URL
```

## 🧠 Gemini Features Used

This project showcases several advanced Gemini capabilities:

### 1. **Step-by-Step Reasoning**
Gemini analyzes errors systematically, breaking down complex issues into:
- Summary → Causes → Diagnostics → Fixes → Confidence

### 2. **Vision Capabilities**
Processes screenshots and images to:
- Extract text from terminal screenshots
- Analyze code in photos
- Understand whiteboard diagrams

### 3. **Structured Output**
Generates valid JSON on demand for:
- API integration
- Automated workflows
- Programmatic consumption

### 4. **Adaptive Confidence**
Provides honest confidence scores (0.0-1.0) based on:
- Information completeness
- Ambiguity in the input
- Certainty of diagnosis

## 📋 How to Use

### In AI Studio:

1. **Choose your input mode**: Text or Image
2. **Provide input**:
   - **Text**: Paste error message or description
   - **Image**: Upload screenshot or photo
3. **Click "Explain"** to get instant analysis
4. **Toggle JSON** if you need structured output

### Example Workflow:

```
1. Developer encounters NullPointerException
2. Pastes stack trace into Smart Explainer
3. Gets immediate analysis:
   - Summary: "Variable is null at line 42"
   - Cause: "Method returned null without check"
   - Fix: "Add null check or use Optional"
   - Confidence: 0.88
4. Developer applies fix in < 2 minutes
```

## 🎬 Demo Video

[Video will be added here - max 3 minutes]

See `demo/demo-script.md` for the complete recording plan.

## 🧪 Testing

We've tested Smart Explainer with:
- ✅ 3 text-based error samples
- ✅ 3 image-based error samples
- ✅ JSON output validation
- ✅ Confidence score accuracy

See `demo/test-results.csv` for detailed test results.

**Target Metrics**:
- Average quality score: ≥ 4.0/5.0
- JSON parse rate: ≥ 90%
- Response time: < 5 seconds

## 🛠️ Technical Details

### Model Configuration

**Text/Image Mode**:
- Model: Gemini 3
- Temperature: 0.25
- Max Tokens: 800
- Streaming: Enabled

**JSON Mode**:
- Model: Gemini 3
- Temperature: 0.0
- Max Tokens: 600
- Format: Strict JSON schema

### Prompt Engineering

Our prompts are designed to:
- Provide consistent, structured output
- Avoid hallucination with confidence scoring
- Give actionable, junior-engineer-friendly advice
- Handle ambiguity gracefully

See `prompts/` directory for full prompt templates.

## 🎯 Use Cases

### For Developers
- Quick error diagnosis during debugging
- Learning from unfamiliar error messages
- Getting second opinions on tricky issues

### For DevOps/SRE
- Analyzing log patterns
- Troubleshooting production incidents
- Documenting common issues

### For Teams
- Onboarding junior engineers
- Building internal knowledge bases
- Standardizing troubleshooting approaches

## 🚧 Future Enhancements

- [ ] Multi-language error message support
- [ ] Historical error pattern matching
- [ ] Integration with issue tracking systems
- [ ] Batch processing for multiple errors
- [ ] Custom prompt templates per team
- [ ] Confidence threshold filtering

## 📄 License

This project is created for the Google AI Hackathon (Devpost submission).

## 🙏 Acknowledgments

Built with:
- **Google AI Studio** - No-code AI app platform
- **Gemini 3** - Advanced language and vision model
- **Devpost** - Hackathon platform

## 📞 Contact

For questions or feedback about this project, please reach out through the Devpost submission page.

---

**Built for Google AI Hackathon 2024**  
*Demonstrating Gemini's reasoning, vision, and structured output capabilities*
