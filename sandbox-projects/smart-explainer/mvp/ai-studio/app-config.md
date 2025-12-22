# AI Studio App Configuration

## Project Setup

**App Name**: Smart Explainer MVP  
**Description**: Gemini-powered error and screenshot explainer with structured output  
**Model**: Gemini 3 (or latest available)

## UI Layout

### Header
- App title: "Smart Explainer"
- Subtitle: "Paste errors, upload screenshots — get instant explanations"

### Input Area
- **Mode Toggle**: Text / Image (radio buttons or tabs)
- **Text Mode**:
  - Large textarea (min 5 rows)
  - Placeholder: "Paste your error message, log excerpt, or technical issue here..."
- **Image Mode**:
  - File upload button
  - Drag-and-drop zone
  - Preview of uploaded image

### Example Buttons
- "Load Java NullPointer Example"
- "Load Port Binding Error"
- "Load Microservice Latency Issue"
- Each button loads corresponding sample from `samples/text-inputs/`

### Action Buttons
- **Explain** (primary button, blue/green)
- **Clear** (secondary button)
- **Toggle JSON** (checkbox or toggle switch)

### Output Panel
- **Human-Readable Mode**:
  - Formatted sections with headers
  - Syntax highlighting for code snippets
  - Confidence score displayed prominently
- **JSON Mode**:
  - Syntax-highlighted JSON
  - Copy button for easy clipboard access

## Model Configuration

### Text Explanation (Human-Readable)
- **Prompt**: Use `prompts/explain-text.prompt.md`
- **Temperature**: 0.25
- **Max Tokens**: 800
- **Top-P**: 0.9
- **Stop Sequences**: None

### Image Explanation
- **Prompt**: Use `prompts/explain-image.prompt.md`
- **Temperature**: 0.25
- **Max Tokens**: 800
- **Vision**: Enabled
- **OCR**: Automatic (if available)

### JSON Mode
- **Prompt**: Use `prompts/explain-json.prompt.md`
- **Temperature**: 0.0
- **Max Tokens**: 600
- **Response Format**: JSON object

## Workflow Logic

### On "Explain" Click:
1. Check current mode (Text vs Image)
2. Validate input (non-empty text or image uploaded)
3. Show loading spinner
4. If JSON toggle is ON:
   - Use `explain-json.prompt.md`
   - Parse response as JSON
   - Display both formatted and raw JSON
5. If JSON toggle is OFF:
   - Use `explain-text.prompt.md` or `explain-image.prompt.md`
   - Display formatted sections
6. Enable streaming if available for better UX

### On Example Button Click:
1. Load corresponding text file content
2. Insert into textarea
3. Switch to Text mode
4. Clear any previous output

### On Clear Click:
1. Clear input area
2. Clear output panel
3. Reset any uploaded images

## Publishing

### Settings
- **Visibility**: Public
- **Sharing**: Anyone with link
- **Analytics**: Enabled (if available)

### Post-Publish
1. Copy public URL
2. Save to `ai-studio/public-link.txt`
3. Test link in incognito/private browser
4. Verify all features work in published version

## Final Acceptance Checklist

- [ ] Public AI Studio link present in `ai-studio/public-link.txt`
- [ ] At least 8 sample inputs tested and documented in `demo/test-results.csv`
- [ ] JSON mode produces valid JSON for test inputs
- [ ] Demo video recorded and placed in `demo/`
- [ ] `prompts/` contains stable prompts (v1)
- [ ] `outputs/` contains at least one human-readable and one JSON sample result
- [ ] README has project summary + demo link

## Troubleshooting

### If outputs are too verbose:
- Add to prompt: "Be concise. Use bullets. Limit each section to 2–4 lines."
- Reduce max tokens to 600

### If hallucinating:
- Add: "If you are guessing, say 'I am guessing' and set confidence ≤ 0.5."
- Lower temperature to 0.1

### If JSON is malformed:
- Set temperature to 0.0
- Add: "You MUST RETURN ONLY JSON, no explanation."
- Test with multiple samples

### If missing root cause:
- Add few-shot examples to prompt
- Increase max tokens slightly
- Version prompts as `explain-text.v2.prompt.md`

## Version History

- **v1.0** (Initial): Basic text and image explanation with JSON toggle
- **v1.1** (Planned): Add confidence threshold filtering
- **v1.2** (Planned): Multi-language support for error messages
