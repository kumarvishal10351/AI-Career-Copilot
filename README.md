# 🧠 AI Career Copilot

> **Transform your resume. Land your dream job.**
> A production-grade AI application built with Streamlit + Mistral AI.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?style=flat-square&logo=streamlit)
![Mistral AI](https://img.shields.io/badge/Mistral_AI-mistral--small-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 **ATS Score** | Overall ATS compatibility score (0–100) |
| 📋 **Section Breakdown** | Score per resume section: Experience, Skills, Education, Formatting, Keywords |
| 🔍 **Skill Gap Analyser** | Visual diff of present vs missing skills |
| 🎯 **Job Match %** | How well the resume matches the job description |
| 🚀 **Smart Suggestions** | Prioritised (High/Medium/Low) improvement actions |
| ✍️ **Resume Improvement** | Full ATS-optimised rewrite powered by Mistral AI |
| 📥 **Export as PDF/TXT** | Download the improved resume in multiple formats |
| 🎯 **Interview Prep** | 13 personalised questions (Technical + Behavioural + Scenario) |
| 🕘 **Session History** | Track all analyses in the current session |
| 🌐 **Multi-role Support** | 15 target roles including SWE, Data Science, ML, DevOps |

---

## 🏗️ Project Structure

```
ai-career-copilot/
├── app/
│   ├── main.py                     # Streamlit entry point + CSS
│   ├── components/
│   │   ├── sidebar.py              # Upload, JD input, role selector
│   │   ├── analysis_tab.py         # ATS analysis UI
│   │   ├── improvement_tab.py      # Resume rewrite UI + export
│   │   ├── interview_tab.py        # Interview questions UI
│   │   └── history_tab.py          # Session history UI
│   ├── services/
│   │   ├── llm_service.py          # Mistral AI wrapper (retry + JSON parsing)
│   │   ├── pdf_service.py          # PDF loading + text extraction
│   │   └── export_service.py       # TXT + PDF export
│   ├── prompts/
│   │   ├── analysis_prompts.py     # ATS analysis prompt templates
│   │   ├── improvement_prompts.py  # Resume rewrite prompt templates
│   │   └── interview_prompts.py    # Interview question prompt templates
│   └── utils/
│       ├── session_manager.py      # Streamlit session_state helpers
│       └── validators.py           # Input validation (API key, PDF, JD)
├── .streamlit/
│   └── config.toml                 # Theme + server config
├── .env.example                    # Environment variable template
├── requirements.txt                # All Python dependencies
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-career-copilot.git
cd ai-career-copilot
```

### 2. Create a virtual environment

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
cp .env.example .env
```

Open `.env` and add your Mistral AI key:

```env
MISTRAL_API_KEY=your_actual_key_here
```

Get a free key at → [console.mistral.ai](https://console.mistral.ai/)

### 5. Run the app

```bash
streamlit run app/main.py
```

Open your browser at **http://localhost:8501**

---

## ☁️ Deployment

### Streamlit Community Cloud (Free)

1. Push your code to a **public GitHub repo**
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repo, branch, and set `app/main.py` as the entry file
4. Add `MISTRAL_API_KEY` under **Advanced settings → Secrets**:
   ```toml
   MISTRAL_API_KEY = "your_key_here"
   ```
5. Click **Deploy** — done in ~2 minutes ✅

### Render.com

```yaml
# render.yaml
services:
  - type: web
    name: ai-career-copilot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app/main.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: MISTRAL_API_KEY
        sync: false
```

### Hugging Face Spaces

1. Create a new Space with **Streamlit** SDK
2. Upload all files
3. Add `MISTRAL_API_KEY` in the Space **Settings → Repository secrets**
4. Rename your entry file to `app.py` and update the import path if needed

---

## ⚙️ Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `MISTRAL_API_KEY` | ✅ Yes | — | Your Mistral AI API key |
| `MISTRAL_MODEL` | No | `mistral-small` | Override the model |
| `DEBUG_LLM` | No | `false` | Enable verbose LLM logging |

---

## 🧠 Architecture & Design Decisions

### LLM Output Strategy
All LLM calls use **system + user** role separation. Analysis and interview features
return **structured JSON** so the app can render rich UI components
(skill tags, score bars, badges) rather than displaying raw text.

### Retry & Resilience
`LLMService._invoke()` implements **exponential back-off** (up to 3 retries)
so transient network errors don't crash the user session.

### Session State
`utils/session_manager.py` centralises all `st.session_state` reads and writes.
This prevents repeated LLM calls when switching tabs — results are cached in
session until the user clicks **Re-analyse** or **Regenerate**.

### PDF Parsing
`services/pdf_service.py` uses **pypdf** with graceful fallback messaging for
encrypted or image-based PDFs that can't be parsed.

### Export
`services/export_service.py` uses **fpdf2** with a fallback to Helvetica
(Latin-1) if the Unicode font files aren't available in the deployment env.

---

## 🔮 Future Upgrades

- [ ] **Vector search** — store past resumes with embeddings, find closest historical match
- [ ] **LinkedIn scraper** — auto-fetch job descriptions from LinkedIn URLs
- [ ] **Multi-language support** — detect and translate non-English resumes
- [ ] **Resume scoring over time** — persistent database (PostgreSQL / Supabase)
- [ ] **Cover letter generator** — one-click tailored cover letters
- [ ] **Mock interview chat** — conversational LLM mock interview
- [ ] **Company research** — auto-research the hiring company and inject context
- [ ] **Salary estimation** — market salary range for the target role + location
- [ ] **Auth** — user accounts with Supabase / Auth0 for cross-session history

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT © 2024 — Feel free to use this in your portfolio or as a foundation for your own product.

---

<div align="center">
  Built with ❤️ using <strong>Mistral AI</strong>, <strong>LangChain</strong>, and <strong>Streamlit</strong>
</div>
