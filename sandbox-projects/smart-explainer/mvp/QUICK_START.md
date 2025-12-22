# Smart Explainer - Quick Start Guide

## 🎯 Goal
Build a working Smart Explainer app in Google AI Studio using the prompts and samples in this repository.

## 📝 Prerequisites
- Google account
- Access to Google AI Studio (https://aistudio.google.com)
- This repository with all prompts and samples

## 🚀 Step-by-Step Implementation

### Step 1: Access AI Studio
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click "Create new" or "New prompt"

### Step 2: Set Up Text Explanation Mode

#### Create the Main Prompt
1. Copy content from `prompts/explain-text.prompt.md`
2. Paste into AI Studio prompt editor
3. Configure model settings:
   - Model: Gemini 3 (or latest)
   - Temperature: 0.25
   - Max output tokens: 800

#### Test with Sample
1. Replace `{{user_text}}` with content from `samples/text-inputs/java-nullpointer.txt`
2. Click "Run" to test
3. Verify output matches format in `outputs/sample-human-readable.md`

### Step 3: Add Image Support

#### Create Image Prompt
1. Create a new prompt or add to existing
2. Copy content from `prompts/explain-image.prompt.md`
3. Enable vision/multimodal input
4. Test with `samples/image-inputs/stacktrace-screenshot.png`

### Step 4: Add JSON Output Mode

#### Create JSON Prompt
1. Create another prompt variant
2. Copy content from `prompts/explain-json.prompt.md`
3. Set temperature to 0.0 for consistent JSON
4. Test and validate JSON output

### Step 5: Build the UI (if using App Builder)

If AI Studio has an app builder interface:

#### Layout
```
┌─────────────────────────────────────┐
│  Smart Explainer                    │
│  Gemini-powered error analysis      │
├─────────────────────────────────────┤
│  [Text] [Image]  Mode Toggle        │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │ Input Area                    │  │
│  │ (Text box or Image upload)    │  │
│  └───────────────────────────────┘  │
│                                     │
│  [Example 1] [Example 2] [Example 3]│
│                                     │
│  [Explain Button]  □ JSON Output    │
├─────────────────────────────────────┤
│  Output Panel                       │
│  ┌───────────────────────────────┐  │
│  │ Summary: ...                  │  │
│  │ Causes: ...                   │  │
│  │ Diagnostics: ...              │  │
│  │ Fix: ...                      │  │
│  │ Confidence: ...               │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

#### Components to Add
1. **Input Toggle**: Switch between text and image input
2. **Text Area**: For pasting error messages
3. **Image Upload**: For screenshots
4. **Example Buttons**: Load sample inputs
5. **Explain Button**: Trigger analysis
6. **JSON Toggle**: Switch output format
7. **Output Panel**: Display results

### Step 6: Wire Up the Logic

#### Text Mode Flow
```
User pastes text → Click Explain → 
  If JSON mode ON:
    Use explain-json.prompt.md
  Else:
    Use explain-text.prompt.md
→ Display formatted output
```

#### Image Mode Flow
```
User uploads image → Click Explain →
  Extract text (OCR if needed) →
  Use explain-image.prompt.md →
  Display analysis
```

#### Example Buttons
```
Click "Java NullPointer" →
  Load samples/text-inputs/java-nullpointer.txt →
  Insert into text area →
  Switch to text mode
```

### Step 7: Test Thoroughly

Use the test matrix in `demo/test-results.csv`:

#### For Each Sample:
1. Load the input (text or image)
2. Click Explain
3. Check output quality (1-5 score):
   - ✅ Summary accurate?
   - ✅ Causes plausible?
   - ✅ Diagnostics actionable?
   - ✅ Fix helpful?
   - ✅ Confidence reasonable?
4. If JSON mode: Validate JSON syntax
5. Record results in CSV

#### Acceptance Criteria:
- Average score ≥ 4.0
- JSON parse rate ≥ 90%
- All 9 samples tested

### Step 8: Publish the App

1. Click "Publish" or "Share" in AI Studio
2. Choose public visibility
3. Copy the public URL
4. Paste URL into `ai-studio/public-link.txt`
5. Test the public link in incognito mode

### Step 9: Record Demo Video

Follow `demo/demo-script.md`:

1. **0-8s**: Title card
2. **8-60s**: Text input demo
3. **60-95s**: Image input demo
4. **95-140s**: JSON toggle demo
5. **140-160s**: Closing with features used

Export as MP4, max 3 minutes, save to `demo/video.mp4`

### Step 10: Prepare Devpost Submission

Gather these materials:

#### Required Files:
- ✅ `demo/video.mp4` - Demo video
- ✅ `demo/screenshots/` - UI screenshots
- ✅ `ai-studio/public-link.txt` - Public app URL
- ✅ `README.md` - Project documentation

#### Devpost Description (200 words):
```
Smart Explainer is an AI-powered debugging assistant that helps 
engineers quickly understand and resolve technical errors. Built 
with Google AI Studio and Gemini 3, it analyzes error messages, 
log excerpts, and screenshots to provide instant, actionable 
explanations.

Key Features:
• Text analysis for error messages and logs
• Image analysis for screenshots and diagrams
• Structured JSON output for automation
• Confidence scoring for transparency

Gemini Capabilities Demonstrated:
1. Step-by-step reasoning - Systematic error analysis
2. Vision - Screenshot and diagram understanding
3. Structured output - Valid JSON generation
4. Adaptive confidence - Honest uncertainty scoring

The app provides:
- One-line summaries
- Root cause analysis (2-3 likely causes)
- Diagnostic steps with exact commands
- Suggested fixes with code snippets
- Confidence scores (0.0-1.0)

Perfect for developers debugging unfamiliar errors, DevOps 
troubleshooting production issues, and teams onboarding junior 
engineers. The structured output enables integration with issue 
tracking and knowledge base systems.

Built entirely in AI Studio with no code required, demonstrating 
the power of prompt engineering and Gemini's advanced capabilities.
```

## 🐛 Troubleshooting

### Issue: Outputs too verbose
**Fix**: Add to prompt: "Be concise. Use bullets. Limit each section to 2–4 lines."

### Issue: Hallucinating or guessing
**Fix**: Add: "If you are guessing, say 'I am guessing' and set confidence ≤ 0.5."

### Issue: Invalid JSON
**Fix**: 
- Set temperature to 0.0
- Add: "You MUST RETURN ONLY JSON, no explanation."
- Test with multiple samples

### Issue: Missing root cause
**Fix**: Add few-shot example to prompt showing desired output

### Issue: Image text unclear
**Fix**: Ensure images are high resolution, good contrast

## 📊 Success Metrics

Track these in `demo/test-results.csv`:

- **Quality Score**: Average ≥ 4.0/5.0
- **JSON Parse Rate**: ≥ 90%
- **Response Time**: < 5 seconds
- **Confidence Accuracy**: Scores align with output quality

## 🎉 You're Done!

Once you've completed all steps:
- ✅ App published and tested
- ✅ Demo video recorded
- ✅ All samples tested
- ✅ Documentation complete
- ✅ Ready for Devpost submission

## 📞 Need Help?

Refer to:
- `ai-studio/app-config.md` - Detailed configuration
- `prompts/` - Prompt templates
- `samples/` - Test inputs
- `outputs/` - Expected outputs

Good luck with your submission! 🚀
