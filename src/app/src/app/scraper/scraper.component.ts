// src/app/scraper/scraper.component.ts

import { Component } from '@angular/core';
import { ScrapingService } from '../scraping.service'; 

@Component({
  selector: 'app-scraper',
  templateUrl: './scraper.component.html',
  styleUrls: ['./scraper.component.css']
})
export class ScraperComponent {
  
  // نموذج البيانات لربطه بحقول الإدخال في HTML (باستخدام [(ngModel)])
  scrapeData = {
    url: '',
    type: 'jobs' // القيمة الافتراضية
  };
  
  // لرسائل الحالة والعرض للمستخدم
  statusMessage: string | null = null;
  statusType: 'success' | 'error' | 'warning' | null = null;
  isLoading: boolean = false;
  
  // قائمة بأنواع التصفية المتاحة
  filterOptions: { value: string, label: string }[] = [
    { value: 'jobs', label: 'وظائف (تستهدف محددات HTML محددة)' },
    { value: 'general', label: 'عام (يتطلب تعديل الكود في Python)' }
  ];

  constructor(private scrapingService: ScrapingService) { }

  /**
   * تُشغل عند إرسال النموذج وتقوم بالاتصال بخدمة Python.
   */
  startScraping(): void {
    if (!this.scrapeData.url) {
      this.statusMessage = 'الرجاء إدخال رابط صالح.';
      this.statusType = 'warning';
      return;
    }

    this.isLoading = true;
    this.statusMessage = 'جارٍ الاتصال بخادم Python وبدء عملية الاستخراج...';
    this.statusType = null;

    this.scrapingService.scrapeData(this.scrapeData.url, this.scrapeData.type)
      .subscribe({
        next: (response) => {
          this.isLoading = false;
          // استقبال الرد من Python وعرضه
          this.statusMessage = response.message;
          this.statusType = response.status;
        },
        error: (err) => {
          this.isLoading = false;
          console.error("خطأ في الاتصال بالخادم:", err);
          this.statusMessage = `فشل الاتصال: تأكد من تشغيل خادم Python على http://localhost:8000 ومن أن إعدادات CORS صحيحة.`;
          this.statusType = 'error';
        }
      });
  }
}
