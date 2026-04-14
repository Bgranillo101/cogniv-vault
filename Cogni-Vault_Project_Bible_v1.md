# Cogni-Vault: Project Specification & Engineering Roadmap

## 1. Project Overview
**Cogni-Vault** is a personal library system where user-uploaded data (PDFs, text, notes) is managed and queried by a team of three autonomous AI agents (Librarian, Analyst, Auditor). The unique value proposition is the **Observable Agentic Architecture**, visualized through a 2D isometric pixel-art library simulation.

## 2. System Design Philosophy (Engineering Focus)
- **Reliability via Redundancy:** Utilizing a multi-agent verification loop (Analyst -> Auditor) to eliminate hallucinations.
- **Asynchronous Event-Driven UI:** Using WebSockets to sync backend agent "thoughts" with frontend sprite animations.
- **Data Integrity:** Implementing Vector RAG (Retrieval-Augmented Generation) with strict source attribution.

## 3. The Tech Stack
- **Frontend:** React (State management) + Phaser.js (Game Engine).
- **Backend:** Python (FastAPI) for asynchronous performance.
- **AI Orchestration:** LangGraph (State Machine for agents).
- **Inference:** Groq API (Llama 3 / Mixtral) for low-latency responses.
- **Database:** Supabase (PostgreSQL + pgvector).
- **Deployment:** Vercel (Frontend) & Render (Backend).

## 4. The Agent Swarm (Personas)
1. **The Librarian (Retriever):** Responsible for semantic search and finding relevant chunks in the Vault.
2. **The Analyst (Synthesizer):** Processes the retrieved data to formulate a comprehensive answer.
3. **The Auditor (Verifier):** Cross-references the answer with original sources; triggers a retry if inaccuracies are found.

## 5. The 6-Phase Roadmap

### Phase 1: Initialize the Vault (Scaffolding)
- Set up Monorepo: `/backend` (FastAPI) and `/frontend` (Vite/React).
- Initialize Phaser.js canvas within a React component.
- **Goal:** A pixel-art character moving on a screen.

### Phase 2: Knowledge Ingestion (ETL Pipeline)
- Connect Supabase and configure `pgvector`.
- Implement PDF upload and text chunking logic in Python.
- **Goal:** Successfully query a document from the database.

### Phase 3: The Brain (LangGraph Implementation)
- Define the Agentic graph in Python.
- Integrate Groq API for sub-second agent reasoning.
- **Goal:** Run a CLI test where agents debate a question based on your data.

### Phase 4: The Neural Link (WebSockets)
- Establish bi-directional communication between FastAPI and React.
- Create event listeners for `AGENT_START`, `AGENT_SEARCH`, `AGENT_RESULT`.
- **Goal:** Real-time log output in the UI as the backend thinks.

### Phase 5: The Visual Library (Animation & UI)
- Map WebSocket events to Sprite animations (Librarian walking, Auditor reading).
- Build the Pixel-art Query Terminal overlay.
- **Goal:** A fully interactive "game" where agents act out the RAG process.

### Phase 6: Final Deployment & Resume Polish
- Deploy both tiers and configure environment variables.
- Write README focusing on "Event-Driven Visual Architecture."
- **Goal:** A live URL to show recruiters.

## 6. Development Tools
- **CLI:** Claude Code (for vibe-coding assistance).
- **IDE:** VS Code.
- **Assets:** Free pixel-art assets from itch.io.
