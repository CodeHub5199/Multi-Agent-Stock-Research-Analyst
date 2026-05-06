# Multi-Agent Stock Research Analyst

**An institutional-grade, multi-agent AI system for Indian equity research.**  
Built with **LangGraph**, **Groq**, **Tavily**, and **yfinance** — it runs parallel specialized agents (Fundamentals, Technical, News) → synthesizes signals → applies a critic layer, and delivers a polished, actionable research report.

![Dashboard Preview](https://via.placeholder.com/800x400/0b0f14/2dd4bf?text=StockMind+Dashboard)  

## ✨ Features

- **Parallel Multi-Agent Architecture** — Fundamentals, Technical Analysis, and News run concurrently
- **Synthesis Agent** — Triangulates signals with weighted consensus scoring
- **Critic Agent** — Stress-tests the thesis, surfaces bear cases, data gaps, and risks
- **Institutional-grade Outputs** — Signal scores, anomaly detection, high-impact events, S/R levels, etc.
- **Live Dashboard** — Modern, responsive single-page UI with animated charts and verdict banners
- **FastAPI Backend** — Async-friendly, production-ready API
- **Indian Market Optimized** — NSE/BSE focus, INR formatting, RBI/SEBI context awareness

## 🏗 Architecture

![Multi-Agent Stock Research Architecture](images/architecture-diagram.png)

*High-level architecture showing parallel agent workflow*

- Fundamental Research Agent (yfinance + LLM)
- Technical Research Agent (yfinance + LLM)
- News Research Agent (Tavily + LLM)
- Synthesis Agent (Consensus + Bull/Bear extraction)
- Critic Agent (Bear case, gaps, risks, confidence audit)

**Key Components:**
- `agents/` — Individual research agents (Pydantic outputs)
- `graph/research_graph.py` — LangGraph state machine
- `api/` — FastAPI layer + models + pipeline
- `templates/dashboard.html` — Self-contained modern frontend

## 🛠 Tech Stack

- **Backend**: FastAPI, LangGraph, LangChain
- **LLM**: Groq (Llama-3 / Mixtral / GPT-OSS models)
- **Search**: Tavily (news)
- **Data**: yfinance
- **Frontend**: Vanilla HTML + Tailwind-like custom CSS (single file)
- **Validation**: Pydantic v2

## 📋 Prerequisites

- Python 3.10+
- Groq API key
- Tavily API key (for news agent)

## 🚀 Installation

1. **Clone the repository**
  ```bash
   git clone https://github.com/yourusername/multi-agent-stock-research.git
   cd multi-agent-stock-research
  ```

2. **Create virtual environment**
  ```bash
   python -m venv venv
   source venv/bin/activate
  ```

3. **Install dependencies**
  ```bash
   pip install -r requirements.txt
  ```

4. Edit ```.env```
 ```env
  GROQ_API_KEY=gsk_...
  TAVILY_API_KEY=tvly-...
  GROQ_MODEL=openai/gpt-oss-120b   # or llama3-70b-8192, mixtral-8x7b-32768, etc.
```
## ▶️ Running the Application

### Development Server

```bash
uvicorn main:app --reload --port 8000
```
Open browser: http://localhost:8000

## 📡 API Usage
## POST /analyze

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "SBIN", "depth": "standard"}'
  ```
Response: Full research state with all agent outputs.

GET ```/health```
Health check endpoint.

GET ```/```
Beautiful interactive dashboard.

## 📊 Sample Tickers

- **Banking**: SBIN, HDFCBANK
- **IT**: INFY, TCS
- **Auto**: TATAMOTORS

## 📁 Project Structure

```text
multi-agent-stock-research/
├── agents/                    # Core research agents
├── api/                       # FastAPI layer
├── graph/                     # LangGraph orchestration
├── templates/
│   └── dashboard.html         # Self-contained UI
├── main.py                    # FastAPI entrypoint
├── requirements.txt
├── .env
└── README.md
```

## ⚠️ Disclaimer

This tool is for research and educational purposes only.
It is not financial advice. Always do your




