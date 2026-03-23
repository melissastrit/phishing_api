import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Ortam değişkenlerini yükle
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# API anahtarını yapılandır
genai.configure(api_key=API_KEY)

app = FastAPI()

# 2. CORS Ayarları (Frontend erişimi için şart)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Veri Şablonu
class EmailRequest(BaseModel):
    text: str

# 4. Ana Sayfa (index.html'i sunar)
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# 5. Analiz Fonksiyonu
@app.post("/analyze")
async def analyze_email(request: EmailRequest):
    if not request.text:
        return {"hata": "Lütfen analiz edilecek bir metin gönderin."}

    try:
        # MODEL TANIMI: En garantili isim budur
        model = genai.GenerativeModel('gemini-1.5-flash')

        # Prompt Mühendisliği
        prompt = f"""
        Sen uzman bir siber güvenlik analistisin. Görevin aşağıda verilen metnin bir oltalama (phishing) veya dolandırıcılık girişimi olup olmadığını analiz etmektir.
        Bana SADECE aşağıdaki JSON formatında cevap ver. Dışına hiçbir metin veya markdown işareti ekleme:
        {{
            "risk_seviyesi": "Düşük/Orta/Yüksek",
            "sebep": "Neden bu puanı verdin? Şüpheli kısımlar neler?"
        }}
        
        Analiz edilecek metin:
        "{request.text}"
        """

        # İstek gönder
        response = model.generate_content(prompt)
        
        # Gelen metni JSON'a çevir (Markdown temizliği yaparak)
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_text)

        return {
            "orijinal_metin": request.text,
            "analiz_sonucu": result
        }

    except Exception as e:
        return {"hata": f"Sistem Hatası: {str(e)}"}