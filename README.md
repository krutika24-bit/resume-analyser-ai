# 📄 Resume Analyser AI

An AI-powered resume analyser built with **Streamlit** and **Claude (Anthropic)**. Upload any resume (PDF, DOCX, or TXT), optionally paste a job description, and get instant, structured feedback.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 ATS Score | How well does your resume pass Applicant Tracking Systems? |
| 🔢 Overall Score | Holistic resume quality score (0–100) |
| 🔍 Skills Gap | Matched skills vs missing skills side-by-side |
| 📑 Section Check | Detects present and missing resume sections |
| 💼 Experience Analysis | Paragraph-level feedback on work history |
| 🎓 Education Analysis | Feedback on education section |
| 🎨 Formatting Tips | Visual and structural improvement suggestions |
| 🚀 Action Items | Prioritised to-do list to improve your resume |

---

## 🗂️ Project Structure

```
resume_analyser/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment variables
└── README.md           # This file
```

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
git clone <your-repo>
cd resume_analyser
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get an Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up / log in
3. Navigate to **API Keys** → **Create Key**
4. Copy the key (starts with `sk-ant-...`)

You can either:
- Paste it directly in the **sidebar** when the app runs, **or**
- Set it as an environment variable (see `.env.example`)

```bash
# macOS/Linux
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Windows (Command Prompt)
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

### 5. Run the app

```bash
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**

---

## 🖥️ How to Use

1. **Enter API Key** — paste your Anthropic API key in the sidebar
2. **Upload Resume** — PDF, DOCX, or plain TXT
3. **Paste Job Description** *(optional)* — for targeted skills gap analysis
4. **Click "Analyse Resume"** — results appear in ~10 seconds
5. **Review all sections** — scores, skills, action items, and more

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `anthropic` | Claude AI API client |
| `pypdf` | PDF text extraction |
| `python-docx` | DOCX text extraction |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| "Could not extract enough text" | PDF may be image/scanned. Use DOCX or TXT instead |
| "API error" | Check API key and credits at console.anthropic.com |
| "Failed to parse JSON" | Rare edge case — just run analysis again |
| App won't start | Run `pip install -r requirements.txt` again |

---

## 🛡️ Privacy

Your resume is sent to the Anthropic API for analysis only. No data is stored anywhere. Each session is fully stateless.

---

## 📄 License

MIT — free to use, modify, and distribute.
