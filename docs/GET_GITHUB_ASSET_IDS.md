# كيفية الحصول على GitHub Asset IDs للفيديوهات

## الطريقة 1: عبر GitHub Issue (الأسهل)

1. **افتح Issue جديد** في المستودع:
   - اذهب إلى: `https://github.com/Hossam-Shehadeh/GeoAI_Assistant/issues/new`
   - أو استخدم Issue موجود

2. **اسحب وأفلت الفيديوهات** في مربع التعليق:
   - اسحب ملف الفيديو من مجلد `media/`
   - أفلته في مربع النص
   - GitHub سيرفع الملف تلقائياً

3. **انسخ رابط الفيديو**:
   - بعد الرفع، سيظهر رابط مثل:
     ```
     https://github.com/user-attachments/assets/abc123def456
     ```
   - انسخ الجزء الأخير: `abc123def456` (هذا هو Asset ID)

4. **استخدم Asset ID في README**:
   - استبدل `video-1`, `video-2`, `video-3` بالـ Asset IDs الفعلية

---

## الطريقة 2: عبر GitHub Release

1. **أنشئ Release جديد**:
   - اذهب إلى: `https://github.com/Hossam-Shehadeh/GeoAI_Assistant/releases/new`
   - أو عدّل Release موجود

2. **ارفع الفيديوهات**:
   - اسحب وأفلت الفيديوهات في قسم "Attach binaries"
   - أو استخدم زر "Choose your files"

3. **احصل على Asset IDs**:
   - بعد الرفع، انقر بزر الماوس الأيمن على الفيديو
   - اختر "Copy link address"
   - الرابط سيكون مثل: `https://github.com/Hossam-Shehadeh/GeoAI_Assistant/releases/download/v1.0/video.mp4`
   - أو استخدم GitHub API للحصول على Asset IDs

---

## الطريقة 3: استخدام Raw GitHub Links (الحالية)

الروابط الحالية تستخدم Raw GitHub links وتعمل بشكل جيد:

```
https://github.com/Hossam-Shehadeh/GeoAI_Assistant/raw/main/media/natural-language-sql-generation-demo.mp4
```

**مميزات Raw Links:**
- ✅ تعمل مباشرة بدون رفع إضافي
- ✅ لا تحتاج إلى Asset IDs
- ✅ سهلة الصيانة

**عيوب Raw Links:**
- ❌ قد تكون أبطأ في التحميل
- ❌ لا تدعم التدفق المباشر (streaming) بشكل جيد

---

## التحديث في README

بعد الحصول على Asset IDs، استبدل في `README.md`:

### قبل:
```
https://github.com/user-attachments/assets/video-1
```

### بعد:
```
https://github.com/user-attachments/assets/abc123def456
```

حيث `abc123def456` هو Asset ID الفعلي من GitHub.

---

## ملاحظات

- **GitHub Assets** أفضل للفيديوهات الكبيرة (أكثر من 10MB)
- **Raw Links** مناسبة للفيديوهات الصغيرة والمتوسطة
- GitHub Assets تدعم **streaming** بشكل أفضل
- Raw Links أسهل في الصيانة والتحديث

---

## الفيديوهات الحالية

1. **Natural Language SQL Generation**: `natural-language-sql-generation-demo.mp4`
2. **Model Builder Converter**: `model-builder-to-python-converter-demo.mp4`
3. **Error Fixing**: `ai-powered-error-fixing-workflow-demo.mp4`

جميعها موجودة في: `media/` folder



