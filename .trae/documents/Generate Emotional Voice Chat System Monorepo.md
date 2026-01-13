I will generate a complete, runnable monorepo for the "Emotional Care Voice Chat System" as requested.

The project will be structured as follows:
- **Root**: Docker Compose, Makefile, Global Config.
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (Async), AI Integrations (Abstracted Providers).
- **Frontend**: Vue 3, TypeScript, Vant UI, Mobile-first.

### Plan Execution Details:

1.  **Project & DevOps Setup**:
    -   Define `docker-compose.yml` for Backend, Frontend (Nginx), MySQL, Redis.
    -   Create `Makefile` for one-command operations.
    -   Define strict `.env` Handling.

2.  **Backend Implementation (Clean Architecture)**:
    -   **Core**: Async Database setup, JWT Auth, Global Exception Handling.
    -   **Domain/Models**: User, Persona (Role), Conversation, Message (with Analysis JSON).
    -   **Services (The "ViewModel")**:
        -   `AuthService`: Login/Register.
        -   `ChatService`: Orchestrate the STT -> LLM -> TTS pipeline.
        -   `Integrations`: `OpenAIClient` (STT/LLM), `IndexTTSClient` (TTS). **Crucial**: Implement a `MockProvider` for all these so the system runs offline immediately.
    -   **API (The "View")**: REST endpoints matching the requirements.
    -   **Background Tasks**: Use `FastAPI.BackgroundTasks` combined with Redis for status tracking to handle the slow AI pipeline asynchronously.

3.  **Frontend Implementation (MVVM)**:
    -   **Setup**: Vite + Vue 3 + TS.
    -   **UI Framework**: Vant (WeChat-like mobile UI).
    -   **Store**: Pinia for State Management (Auth, Chat Session).
    -   **Features**:
        -   Audio Recording (MediaRecorder API).
        -   Chat Interface (Bubbles, Audio Player).
        -   Polling mechanism to check message processing status.

4.  **Data & Storage**:
    -   MySQL for structured data.
    -   Local Volume for Audio Files (mapped to `/static` in backend).

5.  **Deliverables**:
    -   I will output the full file content for all critical files.
    -   I will include a mechanism to generate a dummy `.wav` file on startup so the "Mock TTS" actually plays sound in the browser.

### Verification Strategy:
-   The code will include type hints and standard structure.
-   The "Mock Mode" will be the default configuration to ensure you can run it immediately without API keys.
