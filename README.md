# 🔍 Reddit Sentiment Analysis Dashboard

A real-time sentiment analysis dashboard that fetches Reddit posts by keyword, runs them through a **BERT-based NLP model**, and visualises the results in an interactive Streamlit app.

---

## 📸 Demo
---

## ✨ Features

- **Live Reddit data** — fetches posts across multiple relevant subreddits using the Reddit API (PRAW)
- **BERT sentiment analysis** — classifies posts as Positive, Neutral, or Negative using a pre-trained transformer model
- **Interactive dashboard** with:
  - Key metrics (total posts + sentiment breakdown)
  - Sentiment distribution — pie & bar charts
  - Sentiment over time — smoothed line chart
  - Per-subreddit contribution — stacked bar & pie charts
  - Example posts table for each sentiment category
- **Filters** — slice data by subreddit and date range
- **GPU support** — automatically uses CUDA if available for faster inference
- **Dockerised** — run the whole app with two commands

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web app & dashboard UI |
| [PRAW](https://praw.readthedocs.io) | Reddit API wrapper |
| [Hugging Face Transformers](https://huggingface.co) | BERT sentiment model |
| [PyTorch](https://pytorch.org) | Model inference (CPU/GPU) |
| [Pandas](https://pandas.pydata.org) | Data processing |
| [Plotly](https://plotly.com/python) | Interactive charts |
| [Docker](https://www.docker.com) | Containerised deployment |

---

## ⚙️ Getting Started

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/YOUR_USERNAME/Reddit-Sentiment-Analysis.git
cd Reddit-Sentiment-Analysis
docker build -t sentiment-app .
docker run -p 8501:8501 sentiment-app
```

Then open `http://localhost:8501` in your browser.

### Option 2 — Local Python

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Reddit-Sentiment-Analysis.git
cd Reddit-Sentiment-Analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Reddit API credentials (see below)

# 4. Run the app
streamlit run app.py
```

---

## 🔑 Reddit API Credentials

You'll need a Reddit API key to fetch data. [Register an app here](https://www.reddit.com/prefs/apps).

Create a `.env` file in the project root:

```env
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USER_AGENT=your_user_agent
```

---

## 📖 How It Works

```
User enters keyword
       ↓
PRAW searches Reddit → finds matching subreddits → fetches posts
       ↓
Text cleaned (URLs, mentions, special chars removed)
       ↓
BERT model classifies each post → Positive / Neutral / Negative
       ↓
Results stored in session state → dashboard renders charts & metrics
```

---

## 📁 Project Structure

```
├── app.py              # Streamlit UI & dashboard layout
├── fetch_data.py       # Reddit API integration (PRAW), rate limiting
├── get_sentiment.py    # Text cleaning & BERT sentiment inference
├── utlity.py           # Data filtering, aggregation & Plotly chart builders
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container setup
└── .dockerignore
```

---

## 🚦 Rate Limiting

The app handles Reddit's API rate limits automatically — it monitors remaining requests and pauses when the limit is approached, so you won't hit any 429 errors during large fetches.
