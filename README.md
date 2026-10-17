# CyrusCover

**Where Cinema Meets Legacy** — ابزاری برای پیدا کردن و ذخیره کاور فیلم و سریال، از روی نام فایل یا پوشه.

## ویژگی‌ها
- پشتیبانی از فایل‌های MKV، MP4، AVI و پوشه‌های سریال
- جستجو در IMDb، ویکی‌پدیا و تصاویر وب
- ترجمه خودکار عنوان فارسی به انگلیسی برای جستجوی بهتر
- ذخیره کاور کنار فایل اصلی یا در پوشه دلخواه
- زبان فارسی / انگلیسی و حالت تاریک / روشن

## دریافت برنامه (ویندوز)
فایل اجرایی آماده در پوشه [`exe/`](exe/) قرار دارد: `exe/CyrusCover.exe`
(یا از بخش **Releases** همین مخزن دانلود کنید.) نیازی به نصب پایتون نیست.

## اجرا از سورس
```bash
pip install -r requirements.txt
python CyrusCover.pyw
```

## ساخت فایل اجرایی
روی ویندوز، فایل `build.bat` را اجرا کنید؛ خروجی در `exe\CyrusCover.exe` ساخته می‌شود.

یا با GitHub Actions: این مخزن با هر push روی `main` یا ساخت tag با نام `v*` به‌صورت خودکار exe می‌سازد و در صورت tag، آن را به Release اضافه می‌کند.

## ساختار
```
CyrusCover.pyw        کد اصلی برنامه
assets/cyruscover.ico آیکن برنامه
exe/                  فایل اجرایی ساخته‌شده
build.bat             اسکریپت ساخت exe (ویندوز)
requirements.txt      وابستگی‌ها
```

## سازنده
حسین هادی‌پور — [myhadipour.ir](https://myhadipour.ir) · myhadipour@gmail.com
