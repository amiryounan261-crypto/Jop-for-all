# -*- coding: utf-8 -*-
# server.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware 
import uvicorn
import requests
from bs4 import BeautifulSoup
from airtable import Airtable
import logging

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------------------------------
# 1. إعدادات Airtable والمفاتيح السرية
# ----------------------------------------------------
# مفتاح الـ API (الرمز المميز الذي أرسلته)
AIRTABLE_API_KEY = "PatRqQYzwQwTukmn2.17f8cf65f334dab1f7194113020a5764fa169c36f10b47c19c536475074a8977" 

# معرّف القاعدة (Base ID) الذي أرسلته
AIRTABLE_BASE_ID = "AppSW9R5uCNmRmfl6" 

# تأكد أن هذا الاسم يتطابق تماماً مع اسم الجدول في Airtable
AIRTABLE_TABLE_NAME = "النتائج المستخلصة" 

# ----------------------------------------------------
# 2. تعريف نماذج البيانات
# ----------------------------------------------------
# يحدد شكل البيانات التي يستقبلها الخادم من واجهة Angular
class ScrapingRequest(BaseModel):
    url: str
    type: str # 'jobs' أو 'general'

app = FastAPI()

# ----------------------------------------------------
# 3. إعداد CORS (مهم جداً للاتصال بين Angular و Python)
# ----------------------------------------------------
origins = ["*"] # للسماح لأي مصدر (مثل http://localhost:4200) بالاتصال

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# 4. دوال المنطق الفعلية (Scraping و Airtable)
# ----------------------------------------------------

def send_to_airtable(records_list: list):
    """إرسال السجلات إلى Airtable."""
    if not records_list:
        return True
    try:
        at = Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, api_key=AIRTABLE_API_KEY)
        at.batch_insert(records_list)
        logging.info(f"✅ تم إرسال {len(records_list)} سجل إلى Airtable.")
        return True
    except Exception as e:
        logging.error(f"❌ فشل الإرسال إلى Airtable. الخطأ: {e}")
        return False

def run_job_scraper(target_url: str):
    """منطق استخراج الوظائف (Scraping)"""
    logging.info(f"بدء Scraping للرابط: {target_url}")
    airtable_records = []
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(target_url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        # مثال لمحدد مخصص (يجب تعديله حسب الموقع المستهدف)
        job_listings = soup.find_all('article', class_='job-card-wrapper') 

        for job_item in job_listings:
            title_element = job_item.find('h3', class_='job-card-title')
            link_element = job_item.find('a', class_='job-card-link')
            company_element = job_item.find('div', class_='job-card-company-name')
            
            if title_element and link_element and company_element:
                 record = {
                    "Job_Title": title_element.text.strip(),
                    "Company": company_element.text.strip(),
                    "Link": link_element['href'] 
                }
                 airtable_records.append(record)
        
        return airtable_records

    except requests.exceptions.RequestException as e:
        logging.error(f"❌ خطأ في الاتصال أو الجلب: {e}")
        return []
    except Exception as e:
        logging.error(f"❌ خطأ غير متوقع في Scraping: {e}")
        return []

# ----------------------------------------------------
# 5. نقطة النهاية (API Endpoint)
# ----------------------------------------------------

@app.post("/api/scrape")
async def scrape_data_endpoint(request: ScrapingRequest):
    """تستقبل الرابط ونوع الاستخراج وتقوم بالمعالجة."""
    
    if request.type == 'jobs':
        # 1. تنفيذ Scraping
        scraped_data = run_job_scraper(request.url) 
        
        if not scraped_data:
            return {"status": "warning", "message": "تم الاتصال بالخادم، لكن لم يتم العثور على أي بيانات لاستخراجها."}

        # 2. إرسال إلى Airtable
        success = send_to_airtable(scraped_data)
        
        if success:
            return {
                "status": "success", 
                "message": f"تم استخراج {len(scraped_data)} سجل وإرسالها بنجاح إلى Airtable.",
                "count": len(scraped_data)
            }
        else:
            return {"status": "error", "message": "تم الاستخراج لكن فشل إرسال البيانات إلى Airtable. تحقق من إعدادات Airtable."}

    return {"status": "error", "message": f"نوع الاستخراج ({request.type}) غير مدعوم في الوقت الحالي."}


# ----------------------------------------------------
# 6. نقطة التشغيل الرئيسية
# ----------------------------------------------------

if __name__ == "__main__":
    logging.info("بدء تشغيل خادم FastAPI. الخادم يستمع على المنفذ 8000...")
    # تشغيل الخادم
    uvicorn.run(app, host="0.0.0.0", port=8000)
