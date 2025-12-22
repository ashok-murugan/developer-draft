# Smart Explainer Frontend

Modern Next.js frontend for the Smart Explainer diagnostic platform.

## Features

- **Dual Input Modes**: Text and image-based error analysis
- **Real-time Diagnostics**: Instant structured explanations from Gemini 3
- **Premium UI**: Modern, responsive design with smooth animations
- **Type-Safe**: Full TypeScript implementation
- **API-First**: Thin UI layer consuming backend services

## Tech Stack

- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- React 19

## Setup

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment**:
   Create `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8080
   ```

3. **Run development server**:
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
app/
├── page.tsx              # Main application page
├── layout.tsx            # Root layout with metadata
└── globals.css           # Global styles

components/
└── DiagnosticResult.tsx  # Result display component

services/
└── api.ts                # Backend API client

types/
└── api.ts                # TypeScript type definitions
```

## Usage

### Text Analysis
1. Select "Text Input" tab
2. Paste error message, stack trace, or log
3. Optionally add context (e.g., "java", "python")
4. Click "Analyze"

### Image Analysis
1. Select "Image Input" tab
2. Upload screenshot of error or terminal
3. Optionally add context (e.g., "terminal-error")
4. Click "Analyze"

## Build for Production

```bash
npm run build
npm start
```

## Notes

- Frontend is intentionally thin - no AI logic here
- All reasoning happens in the backend via Gemini
- UI focuses on input collection and result presentation
