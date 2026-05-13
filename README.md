# Fin-VQA — BIST Zeka Terminali

Borsa İstanbul (BIST30 / BIST100) hisseleri için geliştirilmiş, gerçek zamanlı piyasa verilerini Google Gemini'nin çok modlu yapay zekasıyla birleştiren bir analiz terminali. Mum grafik görüntüsünü, teknik göstergeleri, temel metrikleri ve haber akışını tek bir istemde Gemini'ye göndererek Türkçe yapılandırılmış analiz raporu üretir.

---

## Ekran Görüntüleri

### Giriş Ekranı
![Auth Screen](assets/screenshots/Screenshot%202026-05-13%20222619.png)

### Ana Terminal
![Main Terminal](assets/screenshots/Screenshot%202026-05-13%20222708.png)

### Yapay Zeka Analiz Paneli
![AI Analysis](assets/screenshots/Screenshot%202026-05-13%20222841.png)

### Yapay Zeka Sohbet
![AI Chat](assets/screenshots/chat.png)

### BIST Genel Bakış
![BIST Overview](assets/screenshots/Screenshot%202026-05-13%20223005.png)

---

## Özellikler

### Görsel Soru-Cevap (VQA) Motoru
Uygulama, Plotly ile oluşturulan mum grafik görüntüsünü Pillow aracılığıyla Gemini API'ye gönderir. Model, grafiği okumanın yanı sıra temel analiz metriklerini, teknik gösterge değerlerini ve haber başlıklarını da bağlam olarak alarak dört bölümlü yapılandırılmış bir rapor üretir:

- Teknik analiz özeti (destek/direnç, trend yönü)
- Temel analiz değerlendirmesi (F/K, PD/DD, temettü)
- Haber bazlı duygu analizi (Olumlu / Olumsuz / Nötr, 0-100 güven skoru)
- Genel değerlendirme (kısa ve orta vadeli görünüm, risk faktörleri)

### Hisse Kapsamı
- **BIST30** — 31 büyük ölçekli hisse (Türkiye'nin önde gelen şirketleri)
- **BIST100** — BIST30 + 70 ek hisse, toplam 101 sembol
- Sektör kümeleri: Bankacılık, Havacılık, Savunma, Enerji, Teknoloji, Otomotiv ve daha fazlası
- Sektör bazlı **eş hisse karşılaştırması** (peer comparison)

### Teknik Göstergeler
| Gösterge | Parametre | Renk |
|---|---|---|
| RSI | 14 dönem | Teal |
| Hareketli Ortalama | MA20 | Sarı |
| Hareketli Ortalama | MA50 | Mor |

Her gösterge için otomatik sinyal etiketi (Aşırı Alım / Satım, Al / Sat / Nötr) ve görsel progress bar üretilir.

### Temel Analiz Metrikleri
yfinance üzerinden çekilen veriler: güncel fiyat, gün değişimi, 52 hafta yüksek/düşük, piyasa değeri, F/K oranı, PD/DD oranı, EV/FAVÖK, temettü verimi, günlük işlem hacmi ve beta katsayısı.

### Haber Akışı
Google News RSS beslemesinden son 5 haber başlığı, kaynak bilgisi ve yayın tarihi ile birlikte listelenir. Gemini bu haberleri okuyarak genel duygu tonunu raporda değerlendirir.

### Analiz Geçmişi
SQLite tabanlı `analysis_history.db` veritabanı tüm analizleri kaydeder. Kullanıcı geçmiş raporlarını terminal içinden görüntüleyebilir ve yeniden yükleyebilir.

### Yapay Zeka Sohbet
Seçili hissenin mevcut fiyatı, RSI değeri, MA sinyali ve F/K oranı bağlam olarak sağlanır. Kullanıcı Türkçe serbest sorular sorabilir; model kısa ve profesyonel yanıtlar verir. Sık kullanılan sorular için öneri çipleri sunulur.

### Kimlik Doğrulama Katmanı
Giriş Yap / Kayıt Ol sekmeleri ve "Üye olmadan devam et" seçeneği. Oturum bilgileri tarayıcı session state'inde tutulur; harici bir veritabanına bağlantı gerektirmez.

### Arayüz Tasarımı
TradingView estetiğinden ilham alan koyu tema. Inter ve JetBrains Mono tipografi kombinasyonu. CSS değişken sistemi (design tokens) ile tutarlı renk paleti. Tüm Streamlit bileşenleri native CSS override'larla terminal görünümüne uyarlanmış; kenar çubukları, üst çubuk ve Streamlit logosu gizlenmiş.

---

## Gereksinimler

- Python 3.11 veya üzeri
- Google Gemini API anahtarı — [AI Studio'dan alın](https://aistudio.google.com/app/apikey)
- İnternet bağlantısı (yfinance ve Google News RSS için)

---

## Kurulum

```bash
git clone https://github.com/griffinsspike/Fin-VQA.git
cd Fin-VQA
```

Sanal ortam oluşturun ve bağımlılıkları yükleyin:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Yapılandırma

`.env.example` dosyasını kopyalayarak `.env` adıyla kaydedin:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

`.env` dosyasını açıp API anahtarınızı girin:

```
GOOGLE_API_KEY=buraya_kendi_anahtarinizi_yazin
```

API anahtarını `.env` dosyası yerine terminal arayüzündeki "API Key" alanına da girebilirsiniz — uygulama yeniden başlatma gerektirmeden anahtarı session'a alır.

---

## Çalıştırma

```bash
streamlit run app.py
```

Uygulama varsayılan olarak `http://localhost:8501` adresinde başlar.

---

## Kullanım

### 1. Oturum Açma
Uygulamayı ilk açtığınızda kimlik doğrulama ekranı gelir. Kayıt olmak, giriş yapmak veya misafir olarak devam etmek için ilgili seçeneği kullanın.

### 2. API Anahtarı
Navbar'ın sağ bölümündeki model seçiciyi tıklayarak API anahtarınızı girin ve kullanmak istediğiniz Gemini modelini seçin.

### 3. Hisse Seçimi
Üst araç çubuğundaki açılır listeden BIST30 veya BIST100 sembollerinden birini seçin. Şirket adı ve sektör etiketi otomatik olarak görünür.

### 4. Dönem Seçimi
Mum grafik dönemini araç çubuğundaki pill butonlarından ayarlayın: `1M`, `3M`, `6M`, `1Y`, `2Y`, `5Y`.

### 5. Analiz Başlatma
"Yapay Zeka Analizi Çalıştır" düğmesine basın. Uygulama sırasıyla şunları yapar:
1. Mum grafiği PNG görüntüsüne dönüştürür
2. Temel metrikleri ve haberleri biçimlendirilmiş metin olarak hazırlar
3. Teknik gösterge özetini oluşturur
4. Tüm verileri tek bir istemde Gemini'ye gönderir
5. Gelen raporu analiz panelinde ve duygu göstergesinde görüntüler

### 6. Sohbet
Analiz tamamlandıktan sonra sohbet panelinde hisse veya Türk piyasası hakkında Türkçe soru sorabilirsiniz. Öneri çipleri yaygın sorular için hızlı erişim sağlar.

### 7. BIST Genel Bakış
"Piyasaya Genel Bakış" sekmesinde tüm BIST100 hisseleri sektör kartları ve mini grafiklerle listelenir.

---

## Proje Yapısı

```
Fin-VQA/
├── app.py                    # Streamlit giriş noktası; UI, auth katmanı, navbar, layout
├── requirements.txt          # Python bağımlılıkları
├── .env.example              # Ortam değişkeni şablonu
├── .streamlit/
│   └── config.toml           # Streamlit tema ve sunucu ayarları
├── assets/
│   └── screenshots/          # README görsel kaynakları
└── src/
    ├── config.py             # Ticker kayıt defteri, sektör kümeleri, sabitler
    ├── data_pipeline.py      # yfinance OHLCV + temel metrik + haber çekimi
    ├── indicators.py         # RSI, MA20, MA50 hesaplama fonksiyonları
    ├── visualizations.py     # Plotly mum grafik oluşturucu
    ├── vqa_engine.py         # Gemini API köprüsü — analiz ve sohbet
    └── history_manager.py    # SQLite analiz geçmişi yönetimi
```

---

## Gemini Modelleri

Çalışma zamanında iki model arasında geçiş yapılabilir:

| Arayüz Etiketi | Model ID | Önerilen Kullanım |
|---|---|---|
| Pro — Derin Analiz | `gemini-2.5-pro` | Kapsamlı raporlar, karmaşık sorgular |
| Flash — Hızlı Analiz | `gemini-2.5-flash` | Hızlı tarama, düşük gecikme |

---

## Bağımlılıklar

| Paket | Amaç |
|---|---|
| `streamlit` | Web arayüzü çerçevesi |
| `google-generativeai` | Gemini API istemcisi |
| `yfinance` | OHLCV ve temel veri |
| `plotly` | Etkileşimli mum grafikleri |
| `pandas` / `numpy` | Veri işleme |
| `Pillow` | Grafik → görüntü dönüşümü (VQA için) |
| `ta` | Teknik gösterge hesaplamaları |
| `feedparser` | Google News RSS ayrıştırıcı |
| `python-dotenv` | `.env` dosyası okuyucu |
| `kaleido` | Plotly statik görüntü dışa aktarımı |

---

## Yasal Uyarı

Bu uygulama yalnızca bilgilendirme ve araştırma amacıyla geliştirilmiştir. Üretilen analizler ve raporlar yatırım tavsiyesi niteliği taşımaz. Herhangi bir finansal karar vermeden önce kendi araştırmanızı yapmanız ve gerekirse lisanslı bir yatırım danışmanına başvurmanız önerilir.

---

## Lisans

MIT
