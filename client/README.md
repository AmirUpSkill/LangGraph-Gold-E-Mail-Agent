# Cold Email Generator - Frontend

**Canvas-Style UI for Multi-Agent Email Generation**

This is the frontend application for the Cold Email Generator, featuring a modern canvas-style interface with curved branching visualizations that showcase the agentic workflow in real-time.

---

## Overview

The frontend provides an interactive visual representation of the multi-agent email generation process:

- Upload panel for resume and job URL input
- Three branching cards showing parallel agent drafts (Kimi, Qwen, OpenAI OSS)
- Aggregated final card with the synthesized email
- Real-time status updates and metadata display
- Inline editing capabilities
- Dark theme with deep black and silver aesthetic

---

## Tech Stack

- **Framework**: React 18 with Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: ShadCN UI
- **State Management**: Zustand (planned)
- **Data Validation**: Zod
- **HTTP Client**: Fetch API
- **Package Manager**: pnpm

---

## Prerequisites

- Node.js 18 or higher
- pnpm package manager
- Backend API running on `http://localhost:8000` (or configured URL)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/AmirUpSkill/multistage-mail-97415-94834-67025.git
cd multistage-mail-97415-94834-67025
```

### 2. Install dependencies

```bash
pnpm install
```

### 3. Configure environment variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Start the development server

```bash
pnpm dev
```

The application will be available at `http://localhost:5173`

---

## Project Structure

```
src/
├── app/
│   ├── layout.tsx        # Root layout with metadata
│   └── page.tsx          # Main canvas page
├── components/
│   ├── canvas/
│   │   ├── Canvas.tsx           # Main canvas container
│   │   ├── BranchCard.tsx       # Individual agent draft cards
│   │   ├── FinalCard.tsx        # Aggregated result card
│   │   └── UploadPanel.tsx      # Job URL + resume upload
│   └── ui/                      # ShadCN components
├── hooks/
│   └── useEmailGen.ts           # API integration hook
├── lib/
│   └── utils.ts                 # Utility functions
└── types/
    └── api.ts                   # TypeScript API types
```

---

## Available Scripts

```bash
# Development server with hot reload
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests (when configured)
pnpm test

# Lint code
pnpm lint

# Format code
pnpm format
```

---

## Features

### Canvas Interface
- Visual workflow representation
- Curved SVG lines connecting nodes
- Animated transitions between states
- Responsive layout

### Upload Panel
- Drag & drop resume upload (PDF/DOCX)
- Job URL input with validation
- File size and format validation
- Loading states and error handling

### Agent Cards
- Three parallel agent draft displays
- Color-coded by agent (Blue, Green, Pink)
- Metadata display (word count, generation time)
- Status indicators (processing, complete, failed)
- Agent-specific emojis and styling

### Final Card
- Synthesized email display
- Reasoning explanation
- Source breakdown (which agent contributed what)
- Edit functionality
- Copy to clipboard
- Quality score visualization

---

## API Integration

The frontend communicates with the FastAPI backend via REST API:

**Endpoint**: `POST /generate-email`

**Request**:
- Content-Type: `multipart/form-data`
- Body: `job_url` (string), `resume` (file)

**Response**:
```typescript
interface EmailGenerationResponse {
  request_id: string;
  status: "complete" | "processing" | "failed";
  created_at: string;
  inputs: InputContext;
  agent_drafts: AgentDraft[];
  aggregation: AggregationResult;
}
```

See `src/types/api.ts` for complete type definitions.

---

## Styling

### Theme
- **Primary Background**: Deep Black (`#000000`)
- **Secondary Background**: Dark Gray (`#0A0A0A`)
- **Accent**: Silver (`#C0C0C0`)
- **Agent Colors**:
  - Kimi: Blue (`#60A5FA`)
  - Qwen: Green (`#34D399`)
  - OpenAI OSS: Pink (`#F472B6`)

### Tailwind Configuration
Custom theme extensions in `tailwind.config.ts`:
- Custom color palette
- Animation keyframes for canvas elements
- Custom spacing for card layouts

---

## Development

### Adding New Components

```bash
# Add ShadCN components
pnpm dlx shadcn-ui@latest add [component-name]
```

### State Management

Using Zustand for global state (planned):
- Email generation state
- Loading states
- Error handling
- Request history

### Type Safety

All API types are defined in `src/types/api.ts` and synced with backend Pydantic models.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

---

## Troubleshooting

### Cannot connect to backend

**Problem**: API requests fail with network error

**Solution**:
1. Ensure backend is running on `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS configuration in backend

### Build errors

**Problem**: `pnpm build` fails

**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules pnpm-lock.yaml
pnpm install
pnpm build
```

### Type errors

**Problem**: TypeScript errors in API types

**Solution**:
1. Ensure `src/types/api.ts` matches backend schemas
2. Run `pnpm type-check` to identify issues
3. Update types based on latest API contract

---

## Deployment

### Lovable Platform

This project can be deployed via [Lovable](https://lovable.dev/projects/f059bbdc-a084-4a29-b975-67cbf4c0092f):

1. Open the Lovable project
2. Click Share → Publish
3. Configure custom domain (optional)

### Manual Deployment

**Build**:
```bash
pnpm build
```

**Deploy to**:
- Vercel
- Netlify
- AWS Amplify
- Any static hosting service

**Environment Variables**:
Set `NEXT_PUBLIC_API_URL` to your production backend URL.

---

## Contributing

This is part of the Cold Email Generator POC. Contributions are welcome!

---

## License

Educational and demonstration purposes.

---

## Links

- **Lovable Project**: https://lovable.dev/projects/f059bbdc-a084-4a29-b975-67cbf4c0092f
- **Main Repository**: https://github.com/AmirUpSkill/LangGraph-Gold-E-Mail-Agent
- **Backend API Docs**: http://localhost:8000/docs

---

**Built with React, TypeScript, Tailwind CSS, and ShadCN UI**
