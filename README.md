# 🛡️ TruthLayer AI: Document Fact-Checking Web App

TruthLayer AI is a premium, automated document auditing tool that serves as a **Truth Layer** for marketing collateral, pitch decks, whitepapers, and reports. It scans uploaded PDF documents, extracts verifiable factual statements (statistics, dates, financial and technical specs), cross-references them against live web data in real-time, and flags them as **Verified**, **Inaccurate**, or **False** with detailed explanations and reference URLs.

---

## 🌟 Key Features
- **PDF Upload & Text Extraction**: Reads and parses text across all PDF pages.
- **AI-Powered Claim Extraction**: Automatically identifies specific, verifiable claims (figures, percentages, dates) using **Gemini 2.5 Flash**.
- **Double-Layer Live Search**: Queries the live web using a dual pipeline (falling back to a custom-scraped Bing parser if library APIs are rate-limited or blocked).
- **Automated Verification**: Scores claims based on search snippets, returning a verdict, professional rationale, and the correct/updated statistics where applicable.
- **Premium User Dashboard**:
  - Out-of-the-box responsive dashboard with **Truth Score** metrics.
  - Interactive filters by verification status (Verified, Inaccurate, False) and category.
  - Collapsible results cards listing original context, corrected facts, and clickable citation links.
- **Exporting Capabilities**: Download comprehensive reports as **JSON** or **CSV** formats.
- **Pre-Configured default API key** for immediate, friction-free evaluation testing.

---

## 🛠️ Architecture Workflow
```
[ User PDF Upload ]
        │
        ▼ (pypdf)
[ Extracted Raw Text ]
        │
        ▼ (Gemini 2.5 Flash)
[ Verifiable Claims List ] ──(For each claim)──► [ Generate Search Query ]
                                                        │
                                                        ▼ (Bing Search / DDG)
                                                 [ Live Web Snippets ]
                                                        │
                                                        ▼ (Gemini 2.5 Flash)
                                                 [ Verification Verdict ]
                                                        │
                                                        ▼
                                                 [ Inactive Dashboard Report ]
```

---

## 🚀 Getting Started Locally

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Clone and Install Dependencies
Navigate to the directory and run:
```bash
pip install -r requirements.txt
```

### 3. Start the Web App
Run the Streamlit application:
```bash
streamlit run app.py
```
This will spin up a local development server, typically at `http://localhost:8501`.

---

## ☁️ Deployment Guide

### Deploying to Streamlit Cloud (Recommended & Free)
Streamlit Cloud is the fastest and most convenient host for this app.

1. Push this folder (`Factcheck`) to a new public or private **GitHub Repository**. Make sure `app.py`, `factcheck_engine.py`, and `requirements.txt` are at the repository root.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **Create app**, select your repository, branch, and specify `app.py` as the **Main file path**.
4. Click **Deploy!** Your app will be live at a public URL (e.g., `https://truthlayer.streamlit.app`) in under 2 minutes.

*(Optional)*: To secure your own API keys, you can add them to **Streamlit Secrets** by clicking "Settings" -> "Secrets" in your Streamlit Cloud developer console and defining:
```toml
GEMINI_API_KEY = "your-actual-api-key"
```

### Deploying to Render
1. Push your code to GitHub.
2. Log in to [Render](https://render.com) and create a new **Web Service**.
3. Link your repository.
4. Set the following configurations:
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **Deploy**. Render will host the application and expose a public URL.
