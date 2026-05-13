"""
Fin-VQA Engine Module.
Implements the Visual Question Answering bridge to Google Gemini 1.5 Pro/Flash API.
"""

import logging
import re
import time
from datetime import datetime
from typing import Optional

import google.generativeai as genai
from PIL import Image

from src.config import LOG_DATE_FORMAT

logger = logging.getLogger(__name__)


def initialize_model(api_key: str, model_name: str = "gemini-1.5-pro") -> Optional[genai.GenerativeModel]:
    """Initialized the Gemini generative model."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.GenerationConfig(
                temperature=0.4, top_p=0.8, top_k=40, max_output_tokens=4096,
            ),
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        )
        logger.info(f"Gemini model '{model_name}' was initialized successfully.")
        return model
    except Exception as e:
        logger.error(f"Gemini model initialization failed: {e}")
        return None


def build_analysis_prompt(ticker: str, fundamentals_text: str, news_text: str, indicator_summary: dict) -> str:
    """Built a structured analysis prompt for the Gemini API."""
    clean_ticker = ticker.replace(".IS", "")
    rsi = indicator_summary.get("rsi", "N/A")
    rsi_signal = indicator_summary.get("rsi_signal", "N/A")
    ma20 = indicator_summary.get("ma20", "N/A")
    ma50 = indicator_summary.get("ma50", "N/A")
    ma_signal = indicator_summary.get("ma_signal", "N/A")
    price_vs_ma20 = indicator_summary.get("price_vs_ma20", "N/A")
    price_vs_ma50 = indicator_summary.get("price_vs_ma50", "N/A")

    prompt = f"""Sen, BIST hisselerinde uzmanlaşmış kıdemli bir finans analistsin.
{clean_ticker} hissesine ait mum grafik, temel analiz metrikleri, teknik göstergeler ve son haberler sunulmaktadır.

🔍 GÖREVİN:
Aşağıdaki yapıda detaylı bir analiz raporu hazırla:

## 📊 1. TEKNİK ANALİZ ÖZETİ
- Mum grafik fiyat hareketleri, destek/direnç seviyeleri.
- Trend yönü (Yükseliş/Düşüş/Yatay).
- RSI, MA20, MA50 yorumu.
- Kısa ve orta vadeli beklentiler.

## 📈 2. TEMEL ANALİZ ÖZETİ
- F/K ve PD/DD oranları değerlendirmesi.
- Temettü verimi ve finansal sağlık.

## 📰 3. HABER BAZLI DUYGU ANALİZİ
- Haberlerin genel tonu ve etkisi.
- Genel duygu: 🟢 OLUMLU / 🔴 OLUMSUZ / 🟡 NÖTR
- Güven skoru: 0-100

## 🎯 4. GENEL DEĞERLENDİRME
- Risk faktörleri.
- Kısa vadeli (1-4 hafta) ve orta vadeli (1-3 ay) görünüm.

📋 VERİLER:
{fundamentals_text}

TEKNİK GÖSTERGELER:
RSI(14): {rsi} → {rsi_signal} | MA20: {ma20} (Fiyat {price_vs_ma20}) | MA50: {ma50} (Fiyat {price_vs_ma50}) | MA Sinyali: {ma_signal}

{news_text}

⚠️ Yanıtını Türkçe ver. "Yatırım tavsiyesi niteliğinde değildir" ifadesini ekle. Kesin fiyat hedefleri yerine seviye aralıkları kullan.
Analiz: {datetime.now().strftime(LOG_DATE_FORMAT)}"""
    return prompt.strip()


def analyze_stock(chart_image: Image.Image, ticker: str, fundamentals_text: str,
                  news_text: str, indicator_summary: dict, model: genai.GenerativeModel,
                  max_retries: int = 3) -> dict:
    """Performed multimodal stock analysis using the Gemini API."""
    prompt = build_analysis_prompt(ticker, fundamentals_text, news_text, indicator_summary)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"VQA attempt {attempt}/{max_retries} initiated for {ticker}.")
            response = model.generate_content([prompt, chart_image])

            if response and response.text:
                analysis_text = response.text
                sentiment = "NÖTR"
                confidence = 50
                text_lower = analysis_text.lower()

                if any(w in text_lower for w in ["olumlu", "bullish", "yükseliş"]):
                    sentiment = "OLUMLU (Bullish)"
                if any(w in text_lower for w in ["olumsuz", "bearish", "düşüş"]):
                    sentiment = "OLUMSUZ (Bearish)" if sentiment == "NÖTR" else "KARIŞIK (Mixed)"

                for pattern in [r'güven\s*(?:skoru|puanı)\s*[:\s]*(\d+)', r'(\d+)\s*/\s*100']:
                    match = re.search(pattern, text_lower)
                    if match:
                        confidence = min(int(match.group(1)), 100)
                        break

                logger.info(f"VQA completed for {ticker}. Sentiment: {sentiment} ({confidence}%)")
                return {
                    "analysis_text": analysis_text,
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "timestamp": datetime.now().strftime(LOG_DATE_FORMAT),
                    "model_used": model.model_name if hasattr(model, 'model_name') else "gemini",
                    "success": True,
                }
        except Exception as e:
            logger.warning(f"VQA attempt {attempt} failed for {ticker}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)

    logger.error(f"All {max_retries} VQA attempts failed for {ticker}.")
    return {
        "analysis_text": f"⚠️ {ticker} için analiz gerçekleştirilemedi. API anahtarınızı kontrol edin.",
        "sentiment": "N/A", "confidence": 0,
        "timestamp": datetime.now().strftime(LOG_DATE_FORMAT),
        "model_used": "N/A", "success": False,
    }


def chat_with_ai(question: str, context: dict, model: genai.GenerativeModel) -> str:
    """Answers a free-form question about a stock or the Turkish market using Gemini."""
    ticker = context.get("ticker", "")
    price = context.get("price", 0)
    change = context.get("change", 0)
    rsi = context.get("rsi", 50)
    ma_signal = context.get("ma_signal", "Nötr")
    pe = context.get("pe")
    company_name = context.get("company_name", "")
    sector = context.get("sector", "")

    system_ctx = (
        f"Sen Fin-VQA terminalinin yapay zeka asistanısın. "
        f"BIST hisseleri ve Türk piyasaları konusunda uzmansın.\n\n"
        f"Terminaldeki odak hisse:\n"
        f"- {ticker} ({company_name}) — {sector}\n"
        f"- Fiyat: ₺{price:,.2f} ({change:+.2f}%)\n"
        f"- RSI(14): {rsi:.1f} | MA Sinyali: {ma_signal}\n"
        f"- F/K: {f'{pe:.1f}' if pe else 'N/A'}\n\n"
        f"Kısa, net ve profesyonel Türkçe yanıt ver. "
        f"Gerektiğinde 'yatırım tavsiyesi değildir' uyarısını ekle."
    )
    prompt = f"{system_ctx}\n\nSoru: {question}"
    try:
        response = model.generate_content(prompt)
        return response.text if response and response.text else "Yanıt alınamadı."
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return f"Bir hata oluştu: {e}"
