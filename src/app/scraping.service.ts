// src/app/scraping.service.ts

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// تعريف الواجهة لنموذج البيانات الذي سيتم إرساله إلى Python
interface ScrapingPayload {
  url: string;
  type: string;
}

// تعريف الواجهة للرد المتوقع من خادم Python
interface ScrapingResponse {
  status: 'success' | 'error' | 'warning';
  message: string;
  count?: number; // عدد السجلات المستخرجة (اختياري)
}


@Injectable({
  providedIn: 'root'
})
export class ScrapingService {
  // نقطة النهاية لخادم Python الذي يعمل على المنفذ 8000
  private apiUrl = 'http://localhost:8000/api/scrape';

  constructor(private http: HttpClient) { }

  /**
   * يرسل طلب POST إلى خادم Python لتشغيل عملية الاستخراج.
   * @param url الرابط المطلوب استخراجه.
   * @param type نوع الاستخراج (مثل 'jobs', 'general').
   * @returns Observable يحتوي على حالة العملية والرسالة من Python.
   */
  scrapeData(url: string, type: string): Observable<ScrapingResponse> {
    const payload: ScrapingPayload = {
      url: url,
      type: type
    };
    
    // إرسال طلب POST إلى نقطة النهاية
    return this.http.post<ScrapingResponse>(this.apiUrl, payload);
  }
}
