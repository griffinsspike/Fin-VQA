"""
Fin-VQA Configuration Module.
Centralized constants, ticker lists, and styling definitions for the BIST30/100 dashboard.
"""

# ──────────────────────────────────────────────
# BIST30 Index Constituents (Yahoo Finance suffix: .IS)
# Updated periodically by Borsa İstanbul
# ──────────────────────────────────────────────
BIST30_TICKERS = {
    "AKBNK.IS": "Akbank",
    "ARCLK.IS": "Arçelik",
    "ASELS.IS": "Aselsan",
    "BIMAS.IS": "BİM Mağazalar",
    "EKGYO.IS": "Emlak Konut GYO",
    "ENKAI.IS": "Enka İnşaat",
    "EREGL.IS": "Ereğli Demir Çelik",
    "FROTO.IS": "Ford Otosan",
    "GARAN.IS": "Garanti BBVA",
    "GUBRF.IS": "Gübre Fabrikaları",
    "HEKTS.IS": "Hektaş",
    "ISCTR.IS": "İş Bankası (C)",
    "KCHOL.IS": "Koç Holding",
    "KOZAA.IS": "Koza Altın",
    "KOZAL.IS": "Koza Anadolu Metal",
    "KRDMD.IS": "Kardemir (D)",
    "MGROS.IS": "Migros",
    "ODAS.IS": "Odaş Elektrik",
    "OYAKC.IS": "Oyak Çimento",
    "PETKM.IS": "Petkim",
    "PGSUS.IS": "Pegasus",
    "SAHOL.IS": "Sabancı Holding",
    "SASA.IS": "SASA Polyester",
    "SISE.IS": "Şişecam",
    "SOKM.IS": "Şok Marketler",
    "TAVHL.IS": "TAV Havalimanları",
    "TCELL.IS": "Turkcell",
    "THYAO.IS": "Türk Hava Yolları",
    "TKFEN.IS": "Tekfen Holding",
    "TUPRS.IS": "Tüpraş",
    "YKBNK.IS": "Yapı Kredi",
}

# ──────────────────────────────────────────────
# BIST100 – Extends BIST30 with additional constituents
# ──────────────────────────────────────────────
BIST100_EXTRA_TICKERS = {
    "AEFES.IS": "Anadolu Efes",
    "AFYON.IS": "Afyon Çimento",
    "AGESA.IS": "AgeSA Hayat ve Emeklilik",
    "AGHOL.IS": "AG Anadolu Grubu Holding",
    "AKFGY.IS": "Akfen GYO",
    "AKSA.IS": "Aksa Akrilik",
    "AKSEN.IS": "Aksa Enerji",
    "ALARK.IS": "Alarko Holding",
    "ALBRK.IS": "Albaraka Türk",
    "ALFAS.IS": "Alfa Solar Enerji",
    "ALGYO.IS": "ALG GYO",
    "ALTNY.IS": "Altınyağ",
    "ANHYT.IS": "Anadolu Hayat Emeklilik",
    "ANSGR.IS": "Anadolu Sigorta",
    "ASUZU.IS": "Anadolu Isuzu",
    "AYDEM.IS": "Aydem Yenilenebilir Enerji",
    "BAGFS.IS": "Bagfaş",
    "BASGZ.IS": "Başkent Doğalgaz",
    "BIENY.IS": "Bien Yapı",
    "BRISA.IS": "Brisa",
    "BRYAT.IS": "Borusan Yatırım",
    "BUCIM.IS": "Bursa Çimento",
    "CANTE.IS": "Çan2 Termik",
    "CCOLA.IS": "Coca-Cola İçecek",
    "CEMTS.IS": "Çemtaş",
    "CIMSA.IS": "Çimsa",
    "DOAS.IS": "Doğuş Otomotiv",
    "DOHOL.IS": "Doğan Holding",
    "ECILC.IS": "Eczacıbaşı İlaç",
    "EGEEN.IS": "Ege Endüstri",
    "EGSER.IS": "Ege Seramik",
    "ENJSA.IS": "Enerjisa Enerji",
    "ESEN.IS": "Esenboğa Elektrik",
    "GENIL.IS": "Gen İlaç",
    "GESAN.IS": "Giresun Ticaret",
    "GLYHO.IS": "Global Yatırım Holding",
    "GOODY.IS": "Goodyear",
    "GOZDE.IS": "Gözde Girişim",
    "GSDHO.IS": "GSD Holding",
    "HALKB.IS": "Halkbank",
    "HEDEF.IS": "Hedef Holding",
    "IPEKE.IS": "İpek Enerji",
    "ISGYO.IS": "İş GYO",
    "ISMEN.IS": "İş Yatırım Menkul",
    "IZENR.IS": "İzmir Enerji",
    "KARSN.IS": "Karsan Otomotiv",
    "KAYSE.IS": "Kayseri Şeker",
    "KCAER.IS": "KCA Enerji",
    "KLRHO.IS": "Kiler Holding",
    "KONTR.IS": "Kontrolmatik",
    "KONYA.IS": "Konya Çimento",
    "KORDS.IS": "Kordsa",
    "LOGO.IS": "Logo Yazılım",
    "MAVI.IS": "Mavi Giyim",
    "MPARK.IS": "MLP Sağlık",
    "NETAS.IS": "Netaş Telekom",
    "OBAMS.IS": "Oba Makarna",
    "OTKAR.IS": "Otokar",
    "OYAKC.IS": "Oyak Çimento",
    "PAPIL.IS": "Papilon Savunma",
    "PENTA.IS": "Penta Teknoloji",
    "QUAGR.IS": "QUA Granite",
    "SARKY.IS": "Sarkuysan",
    "SELEC.IS": "Selçuk Ecza Deposu",
    "SKBNK.IS": "Şekerbank",
    "SMRTG.IS": "Smart Güneş Enerjisi",
    "TATGD.IS": "Tat Gıda",
    "TMSN.IS": "Tümosan Motor",
    "TOASO.IS": "Tofaş",
    "TRGYO.IS": "Torunlar GYO",
    "TTKOM.IS": "Türk Telekom",
    "TTRAK.IS": "Türk Traktör",
    "TUKAS.IS": "Tukaş",
    "TURSG.IS": "Türkiye Sigorta",
    "ULKER.IS": "Ülker Bisküvi",
    "VAKBN.IS": "Vakıfbank",
    "VESBE.IS": "Vestel Beyaz Eşya",
    "VESTL.IS": "Vestel Elektronik",
    "YATAS.IS": "Yataş",
    "YEOTK.IS": "Yeo Teknoloji",
    "ZOREN.IS": "Zorlu Enerji",
}

# Merged BIST100 = BIST30 + extras
BIST100_TICKERS = {**BIST30_TICKERS, **BIST100_EXTRA_TICKERS}

# ──────────────────────────────────────────────
# Claude Design Palette
# Deep Navy + Teal Accent + Glassmorphism
# ──────────────────────────────────────────────
COLORS = {
    # Candlestick
    "up": "#10b981",
    "down": "#ef4444",
    "doji": "#475569",

    # Surfaces
    "bg_primary": "#080c14",
    "bg_surface": "#0d1220",
    "bg_elevated": "#111827",
    "bg_hover": "#1e293b",
    "border": "rgba(255,255,255,0.08)",
    "border_subtle": "rgba(255,255,255,0.04)",

    # Text
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_tertiary": "#475569",
    "text_inverse": "#080c14",

    # Accents
    "teal": "#00d4aa",
    "teal_dim": "rgba(0,212,170,0.15)",
    "accent": "#3b82f6",
    "accent_dim": "rgba(59,130,246,0.12)",
    "purple": "#8b5cf6",
    "positive": "#10b981",
    "negative": "#ef4444",
    "warning": "#f59e0b",
    "neutral": "#94a3b8",

    # Indicators
    "ma20": "#f59e0b",
    "ma50": "#6366f1",
    "rsi": "#8b5cf6",
    "volume": "#1e293b",

    # Legacy aliases
    "bg_secondary": "#0d1220",
    "bg_card": "#111827",
    "gold": "#00d4aa",
    "text_gold": "#00d4aa",
    "bullish": "#10b981",
    "bearish": "#ef4444",
}

# ──────────────────────────────────────────────
# Chart Configuration
# ──────────────────────────────────────────────
CHART_CONFIG = {
    "height": 480,
    "font_family": "'Inter', -apple-system, sans-serif",
    "gridcolor": "rgba(255, 255, 255, 0.04)",
    "line_width": 2,
    "candle_width": 0.6,
}

# ──────────────────────────────────────────────
# Sector Clustering (for Peer Comparison)
# ──────────────────────────────────────────────
SECTOR_CLUSTERS = {
    "Havacılık": ["THYAO.IS", "PGSUS.IS", "TAVHL.IS"],
    "Savunma": ["ASELS.IS", "ALTNY.IS", "OTKAR.IS"],
    "Teknoloji & Yazılım": ["MIATK.IS", "LOGO.IS", "ARDYZ.IS", "TCELL.IS"],
    "Enerji & Yenilenebilir": ["SMRTG.IS", "ALFAS.IS", "ASTOR.IS", "GESAN.IS", "ENJSA.IS"],
    "Petrokimya & Sanayi": ["TUPRS.IS", "PETKM.IS", "ENKAI.IS", "SASA.IS"],
    "Bankacılık": ["AKBNK.IS", "GARAN.IS", "ISCTR.IS", "YKBNK.IS"],
    "Holding": ["KCHOL.IS", "SAHOL.IS", "TKFEN.IS", "ALARK.IS"],
    "Perakende": ["BIMAS.IS", "MGROS.IS", "SOKM.IS"],
    "Demir & Çelik": ["EREGL.IS", "KRDMD.IS"],
    "Otomotiv": ["FROTO.IS", "TOASO.IS", "DOAS.IS", "KARSN.IS"],
}


def get_sector_for_ticker(ticker: str) -> str:
    """Returned the sector cluster name for a given ticker."""
    for sector, tickers in SECTOR_CLUSTERS.items():
        if ticker in tickers:
            return sector
    return "Diğer"


def get_peers_for_ticker(ticker: str) -> list[str]:
    """Returned peer tickers in the same sector cluster."""
    for _sector, tickers in SECTOR_CLUSTERS.items():
        if ticker in tickers:
            return [t for t in tickers if t != ticker]
    return []


# ──────────────────────────────────────────────
# Period Options
# ──────────────────────────────────────────────
PERIOD_OPTIONS = {
    "1M": "1mo",
    "3M": "3mo",
    "6M": "6mo",
    "1Y": "1y",
    "2Y": "2y",
    "5Y": "5y",
}

# ──────────────────────────────────────────────
# Gemini Model Options
# ──────────────────────────────────────────────
GEMINI_MODELS = {
    "Pro — Deep Analysis": "gemini-2.5-pro",
    "Flash — Fast Analysis": "gemini-2.5-flash",
}

# ──────────────────────────────────────────────
# Logging & Reporting Constants
# ──────────────────────────────────────────────
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CACHE_TTL_SECONDS = 300  # 5 minutes
NEWS_COUNT = 5
RSI_PERIOD = 14
MA_SHORT = 20
MA_LONG = 50
