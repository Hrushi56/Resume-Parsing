# GruntWorkr: AI-Powered Multi-Agent Talent Intelligence

GruntWorkr is a modern, AI-driven platform designed to streamline the recruitment process through intelligent resume parsing, skill normalization, and candidate matching. Built with a multi-agent orchestration architecture, it leverages cutting-edge LLMs to provide precise talent insights.

---

## 🚀 Key Features

- **Multi-Agent Parsing:** Specialized agents to extract personal info, experience, and education with high accuracy.
- **Intelligent Skill Mapping:** Automatically normalizes extracted skills against a central taxonomy.
- **Candidate-Job Matching:** Advanced matching algorithms to find the best fit for specific roles.
- **Real-time Telemetry:** Built-in tracking for performance monitoring and API health.
- **Modern Dashboard:** A sleek, responsive interface for managing the entire talent pipeline.

## 🛠️ Tech Stack

### Backend
- **Framework:** FastAPI (Python)
- **Orchestration:** Custom Multi-Agent Pipeline
- **Database:** SQLite
- **Intelligence:** Groq & HuggingFace Integration

### Frontend
- **Framework:** React + TypeScript
- **Bundler:** Vite
- **Styling:** Vanilla CSS / Modern UI components

---

## ⚙️ Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js & npm

### 2. Environment Setup
Create a `.env` file in the root directory (refer to `.env.example`):
```env
GROQ_API_KEY=your_key_here
HF_TOKEN=your_token_here
```

### 3. Backend Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```
The API will be available at `http://localhost:8000`.

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

## 📂 Project Structure

- `agents/`: specialized AI agents for different parsing tasks.
- `api/`: FastAPI route definitions and controllers.
- `database/`: database schema and connection management.
- `frontend/`: React source code and assets.
- `taxonomy/`: skill hierarchy and normalization data.
- `utils/`: shared helpers, telemetry, and logging.

---

## 📄 License
This project is for demonstration purposes. (Add your license here)
