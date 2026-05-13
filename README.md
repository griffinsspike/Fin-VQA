# Fin-VQA — BIST Intelligence Terminal

A Streamlit-based financial intelligence terminal for Borsa Istanbul (BIST) stocks. It combines real-time market data, technical analysis, and Google Gemini's multimodal AI to deliver chart-aware analysis reports and an interactive AI chat interface.

## Features

- **Visual Question Answering** — Sends candlestick chart images to Gemini (Pro or Flash) alongside fundamental data, technical indicators, and news headlines to generate structured Turkish-language analysis reports.
- **BIST30 / BIST100 Coverage** — Full ticker registry with sector clustering and peer-comparison groupings.
- **Technical Indicators** — RSI(14), MA20, MA50 with signal labels and Plotly candlestick charts.
- **Fundamental Data** — P/E, P/B, dividend yield, market cap, and more via yfinance.
- **News Sentiment** — Google News RSS headlines with sentiment classification (Bullish / Bearish / Neutral) and a 0–100 confidence score.
- **Analysis History** — SQLite-backed storage of past reports with replay and export.
- **AI Chat** — Context-aware free-form chat about the selected stock or the broader Turkish market.
- **TradingView-style UI** — Dark theme with Inter + JetBrains Mono typography and a CSS design-token system.

## Prerequisites

- Python 3.11 or later
- A Google Gemini API key ([obtain one here](https://aistudio.google.com/app/apikey))

## Installation

```bash
git clone https://github.com/griffinsspike/Fin-VQA.git
cd Fin-VQA

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Copy the example environment file and fill in your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
GOOGLE_API_KEY=your_google_api_key_here
```

The application reads this key at startup via `python-dotenv`. It is also possible to supply the key directly inside the terminal's API key input field — no restart required.

## Running

```bash
streamlit run app.py
```

The terminal is served at `http://localhost:8501` by default.

## Project Structure

```
Fin-VQA/
├── app.py                  # Streamlit entry point, UI layout, auth gate
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .streamlit/
│   └── config.toml         # Streamlit theme and server settings
└── src/
    ├── config.py           # Ticker registry, sector clusters, constants
    ├── data_pipeline.py    # yfinance OHLCV + fundamentals + news fetching
    ├── indicators.py       # RSI, MA20, MA50 calculation utilities
    ├── visualizations.py   # Plotly candlestick chart builder
    ├── vqa_engine.py       # Gemini API bridge — analysis and chat
    └── history_manager.py  # SQLite analysis history storage
```

## Models

The application supports two Gemini models selectable at runtime:

| Label | Model ID | Recommended For |
|---|---|---|
| Pro — Deep Analysis | `gemini-2.5-pro` | Thorough reports, complex queries |
| Flash — Fast Analysis | `gemini-2.5-flash` | Quick scans, lower latency |

## Disclaimer

This tool is for informational and research purposes only. Nothing produced by this application constitutes investment advice. Always conduct your own due diligence before making financial decisions.

## License

MIT
