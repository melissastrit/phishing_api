import os
import json
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# Şifremizi güvenle yüklüyoruz
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

app = FastAPI()
@app.get("/")
async def read_index():
    return FileResponse('index.html')
# 1. CORS Ayarları (Frontend uygulamalarının bu API'ye erişmesine izin verir)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Gerçek projelerde buraya sadece kendi sitemizin linki yazılır
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Pydantic Modeli (Gelecek verinin şablonunu ve kurallarını belirliyoruz)
class EmailRequest(BaseModel):
    text: str

@app.post("/analyze")
def analyze_email(request: EmailRequest):
    if not request.text:
        return {"hata": "Lütfen analiz edilecek bir metin gönderin."}
# Modeli burada, fonksiyonun tam içinde tanımlayalım
    model = genai.GenerativeModel('gemini-1.5-flash')
    # 3. Prompt Engineering: Yapay zekayı bir JSON formatına zorluyoruz
    prompt = f"""
    Sen uzman bir siber güvenlik analistisin. Görevin aşağıda verilen metnin bir oltalama (phishing) veya dolandırıcılık girişimi olup olmadığını analiz etmektir.
    Bana SADECE aşağıdaki JSON formatında cevap ver. Dışına hiçbir metin veya markdown işareti ekleme:
    {{
        "risk_seviyesi": "Düşük/Orta/Yüksek",
        "sebep": "Neden bu puanı verdin? Şüpheli kısımlar neler?"
    }}
    
    Analiz edilecek metin:
    {request.text}
    """

    try:
        # Yapay zekaya istek atarken "bana sadece JSON dön" kuralını ekliyoruz
       
            response = model.generate_content(prompt)
            yapay_zeka_json = json.loads(response.text)
        
            return {
            "orijinal_metin": request.text,
            "analiz_sonucu": yapay_zeka_json
        }
    except Exception as e:
        return {"hata": f"Sistem Hatası: {str(e)}"}