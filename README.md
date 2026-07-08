<div align="center">
  <h1><strong> Autonomous Insurance Claims Processing Agent</strong></h1>
</div>

<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini LLM" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</div>

<br>

This agent is a state-of-the-art First Notice of Loss (FNOL) automation engine designed to drastically reduce manual overhead in the insurance lifecycle. By leveraging multi-modal LLM extraction pipelines, it ingests raw unstructured claims documents, maps them to strict deterministic JSON schemas, and dynamically calculates optimal processing routes (e.g., Fast-track, Specialist Queue). The architecture provides immediate, scalable document intelligence wrapped in an ultra-premium, zero-friction user interface.

---

## User Interface & Experience

| Component | UI Design Styling | Functional Highlight |
| :--- | :--- | :--- |
| **Monochrome Architecture** | Deep black `#000000` backgrounds with high-contrast `#ffffff` foregrounds and micro-animations. | Ensures hyper-focused readability and minimizes cognitive load during high-density data review. |
| **Dynamic Routing Badges** | Glassmorphic, translucent containers with contextual semantic highlighting. | Visually isolates the predicted decision route (e.g., green for Fast-track, red for Manual Review). |
| **Data Extraction Grid** | Flexbox-driven masonry layout with strict typography mapping and deterministic spacing. | Surfaces AI-extracted metadata instantly. Missing fields are injected with high-visibility bold red `NULL` identifiers. |
| **Interactive Code Viewer** | Greyscale-themed, syntax-highlighted block with horizontal scroll and DOM injection. | Allows developers and auditors to seamlessly inspect the raw, structured JSON response emitted by the LLM pipeline. |

---

## Technical Pillars & Key Features

| Technical Pillar | Technology | Functional Specification |
| :--- | :--- | :--- |
| **Deterministic Data Extraction** | Google LLM API / Prompt Engineering | Utilizes few-shot prompting to force the LLM to output valid, structured JSON without conversational hallucination. |
| **Intelligent Document Routing** | Logic Layer / Heuristics Engine | Calculates decision routes (Fast-track, Investigation, Specialist) based on parsed severity thresholds and missing data flags. |
| **Client-Side State Persistence** | JavaScript `sessionStorage` API | Persists the complex JSON payload and DOM state across browser reloads, guaranteeing zero data loss during user sessions. |
| **Zero-Dependency Frontend** | Vanilla CSS3 / ES6 JavaScript | Built strictly without heavyweight frameworks (No React/Vue). Employs CSS Variables (`:root`) for instant, cascading theme manipulation. |

---

## System Architecture

```mermaid
graph TD
    classDef frontend fill:#1e1e1e,stroke:#ffffff,stroke-width:2px,color:#ffffff;
    classDef backend fill:#0f172a,stroke:#34d399,stroke-width:2px,color:#ffffff;
    classDef ai fill:#312e81,stroke:#c084fc,stroke-width:2px,color:#ffffff;
    classDef storage fill:#1e1e1e,stroke:#60a5fa,stroke-width:2px,color:#ffffff;

    subgraph Client ["Presentation Layer"]
        UI["Web Interface (HTML/CSS/JS)"]:::frontend
        State["Session Storage"]:::storage
    end

    subgraph Core ["Processing Core"]
        API["FastAPI / Flask Backend"]:::backend
        PDF["Document Parser (PDF/Images)"]:::backend
    end

    subgraph Intelligence ["LLM Engine"]
        LLM["Google AI Studio API"]:::ai
        Prompts["Prompt Engineering Module"]:::ai
    end

    UI -->|"Uploads Document"| API
    API -->|"Extracts Raw Text"| PDF
    PDF -->|"Sends Context"| Prompts
    Prompts -->|"Queries Model"| LLM
    LLM -->|"Returns Structured JSON"| API
    API -->|"Delivers FNOL Payload"| UI
    UI -->|"Persists Data"| State
```

---

## 📂 Project Directory Structure

```ascii
Autonomous-Agent/
├── app/                        # Backend Application Core
│   ├── prompts/                # LLM System Prompts
│   │   └── extraction_prompt.txt
│   ├── services/               # Core Logic & Utilities
│   │   └── pdf_reader.py       # OCR & PDF Parsing Engine
│   ├── config.py               # Environment & Global Configurations
│   └── main.py                 # API Entrypoint
├── static/                     # Static Assets
│   ├── css/
│   │   └── style.css           # Global Stylesheet & Glassmorphism UI
│   └── js/
│       └── main.js             # Client-side Logic & DOM Manipulation
├── templates/                  # View Templates
│   └── index.html              # Main Single-Page Application (SPA)
├── .env.example                # Template for Environment Variables
├── .gitignore                  # Git Ignored Files
├── requirements.txt            # Python Dependencies
└── README.md                   # Project Documentation
```

---

## Setup & Installation Guide

### Prerequisites
Ensure you have the following installed locally:
- Python 3.10+
- Git

### 1. Clone & Environment
```bash
# Clone the repository
git clone https://github.com/Levi9633/Autonomous-Insurance-Claims-Processing-Agent.git
cd Autonomous-Insurance-Claims-Processing-Agent

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy the environment template
cp .env.example .env
```
Open the `.env` file and insert your required API keys (e.g., `GOOGLE_API_KEY`).

### 3. Booting Local Development Server
```bash
# Run the application (using Uvicorn/FastAPI or Flask)
uvicorn app.main:app --reload
# OR for Flask: python app/main.py
```
The application will be accessible at `http://127.0.0.1:8000`.

---

## Verification and Testing

To ensure the environment is configured properly and the LLM pipeline is active, run the test suite:

```bash
# Execute unit tests for the PDF parser and prompt construction
pytest tests/

# Expected Output:
# ===================== test session starts =====================
# collected 12 items
# tests/test_pdf_reader.py ....                           [ 33%]
# tests/test_extraction.py ........                       [100%]
# ====================== 12 passed in 1.4s ======================
```

You can also run a manual validation check by uploading a sample PDF claim document through the UI and verifying that the `Fast-track` or `Manual Review` status correctly highlights missing parameters via the `.null-value` red injection.
