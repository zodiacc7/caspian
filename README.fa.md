<div dir="rtl" align="right">

# Caspian-BYOC

[**دانلود آخرین نسخه**](https://github.com/Iman/caspian/releases/latest) | [**باز کردن ویکی**](https://github.com/Iman/caspian/wiki/Home.fa)

<div dir="ltr" align="left">

[English](README.md) | [فارسی](README.fa.md) | [Русский](README.ru.md) | [中文](README.zh.md) | [العربية](https://github.com/Iman/caspian/wiki/Home.ar) | [اردو](https://github.com/Iman/caspian/wiki/Home.ur) | [Türkçe](https://github.com/Iman/caspian/wiki/Home.tr)

</div>

<div dir="ltr" align="left">

[![ci](https://github.com/Iman/caspian/actions/workflows/ci.yml/badge.svg)](https://github.com/Iman/caspian/actions/workflows/ci.yml) [![release](https://img.shields.io/github/v/release/Iman/caspian?label=release)](https://github.com/Iman/caspian/releases/latest) [![licence AGPL-3.0-or-later](https://img.shields.io/badge/licence-AGPL--3.0--or--later-blue)](LICENSE) [![platform Windows, macOS, Raspberry Pi and Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Raspberry%20Pi%20%7C%20Linux-blue)](https://github.com/Iman/caspian/releases/latest) [![container](https://img.shields.io/badge/ghcr.io-caspian-blue)](https://github.com/Iman/caspian/pkgs/container/caspian) [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Iman/caspian)

</div>

![دستگاه‌های شما به وای‌فای جعبه وصل می‌شوند. جعبه با کانفیگی که پیست کرده‌اید وصل می‌شود و همه چیز را به سرورِ خودتان در خارج تونل می‌کند، پس مودمِ خانه و شرکتِ اینترنتی فقط یک اتصالِ رمزگذاری‌شده به یک آدرس می‌بینند، نه اینکه شما چه باز می‌کنید.](docs/images/flow-fa.svg)

Caspian-BYOC یک کامپیوتر Windows، یک Mac با macOS، یک Raspberry Pi یا یک
دستگاه Linux را به دروازهٔ وای‌فای تبدیل می‌کند که کانفیگش را خودتان می‌آورید.
یک کانفیگ سازگار با V2Ray یا Xray را در پنل وب پیست کنید و یک کلید را بزنید.
Caspian لینک‌های VLESS،
VMess، Shadowsocks، SOCKS، Trojan و Hysteria2 را می‌پذیرد. فایل‌های YAML مربوط
به Clash و Clash.Meta، فایل JSON خامِ Xray، فهرست لینک‌ها و اشتراک base64 نیز
پذیرفته می‌شوند. Caspian با Xray-core وصل می‌شود و تونل را به شکل هات‌اسپات
وای‌فای پخش می‌کند، پس هر دستگاهی که وصل شود بدون نصب برنامه محافظت می‌شود.
کنترل‌های اختیاری ضد DPI (عبور از DPI)، یعنی جعل SNI و تکه‌کردن TLS، کمک می‌کنند اتصال در شبکه‌هایی که ترافیک را بازرسی می‌کنند برقرار شود.

![پنل کاسپین، متصل](docs/images/panel-fa.png)

تصویرِ بالا یک اسکرین‌شاتِ واقعی از یک دستگاهِ در حالِ کار است، گرفته‌شده روی یک
Raspberry Pi 5 در تاریخ 2026-09-03 با تونلِ بالا و پیش از آنکه دستگاهی وصل شود.
رمزِ شبکه، نامِ کانفیگ و آدرسِ سرور در آن جایگزین شده‌اند، و کدِ تصویریِ اتصال تار
شده، چون آن کد نامِ شبکه و رمزش را در خودش دارد. هیچ چیزِ دیگری تغییر نکرده است.

پنل به‌صورت پیش‌فرض انگلیسی است. از فهرست زبان در بالای صفحه، فارسی را انتخاب کنید. هیچ حسابی در کار نیست، هیچ داده‌ای از شما
فرستاده نمی‌شود، و پنل به خودی خود چیزی از اینترنت نمی‌گیرد، مگر آنکه شما روی
نشانی اشتراکی که ذخیره کرده‌اید دکمهٔ تازه‌سازی را بزنید.

![Caspian Control در Windows](docs/images/caspian-control-windows.png)

![Caspian Control در macOS](docs/images/caspian-control-macos.png)

## ضد DPI: جعل SNI و تکه‌کردن TLS

بازرسی عمیق بسته (DPI) روشی است که شبکه با آن آغاز یک اتصال را می‌خواند تا تصمیم بگیرد آن را مسدود کند یا نه. کاسپین سه کنترل اختیاری ضد DPI (عبور از DPI) دارد که در پنل، کنار پیکربندی ذخیره‌شده، قرار گرفته‌اند:

- **نام سرور جعلی.** کاسپین پیش از جریان واقعی پراکسی یک سلام TLS می‌فرستد که نام یک دامنهٔ پوششی را دارد. نام واقعی سرور TLS یا REALITY و بررسی گواهی دقیقاً همان‌طور که بود می‌ماند.
- **تکه‌کردن TCP.** نخستین سلام TLS در دو نوشتار می‌رود که نزدیک میانهٔ نام سرور از هم جدا شده‌اند.
- **تکه‌کردن رکورد TLS.** رکورد سلام در همان نقطه تقسیم می‌شود، بدون آنکه محتوای دست‌دهی تغییر کند.

هر کنترل مستقل است و می‌تواند با دیگران ترکیب شود. ذخیره‌کردن، تونل روشن را با تنظیم تازه دوباره وصل می‌کند. این کنترل‌ها با VLESS، VMess و Trojan روی انتقال‌های پشتیبانی‌شدهٔ TCP در IPv4 کار می‌کنند و دو تکه‌کردن به TLS معمولی نیاز دارند.

عبور از DPI به شبکه و قواعد فیلترینگ آن بستگی دارد. کاسپین نامرئی بودن یا ایمنی همگانی در برابر DPI را وعده نمی‌دهد. آزمون‌های حلقهٔ محلی دادهٔ بدون تغییر، دست‌دهی واقعی TLS و رد نام نادرست گواهی را بررسی می‌کنند؛ عبور از محدودیت ارائه‌دهندهٔ اینترنت را ثابت نمی‌کنند. [تنظیم SNI، سکوها و محدودیت‌ها](docs/SNI.fa.md) و [پژوهش و انتساب بالادستی](docs/THIRD-PARTY.fa.md) را ببینید.

## پراکسی بالادستی SOCKS5

کاسپین می‌تواند اتصال به سرور تونلی که در کانفیگ خود وارد کرده‌اید را، به‌صورت اختیاری، از یک پراکسی SOCKS5 بالادستی عبور دهد. این پراکسی **فقط مسیر برقراری اتصال تونل است** و جای تونل اصلی را نمی‌گیرد: ترافیک دستگاه‌های کاربر همچنان طبق مسیریابی عادی کاسپین وارد outbound مربوط به VLESS، VMess، Shadowsocks، SOCKS، Trojan یا Hysteria2 می‌شود.

به **Advanced → Upstream SOCKS5** بروید، آن را فعال کنید و آدرس و پورت پراکسی را وارد کنید. نام کاربری و رمز عبور اختیاری هستند. ذخیرهٔ تنظیمات، تونل در حال اجرا را با تنظیمات جدید دوباره وصل می‌کند.

نمونه:

<div dir="ltr" align="left">

```text
Address: 127.0.0.1
Port:    1080
Username: optional
Password: optional
```

</div>

رمز عبور دوباره در صفحه نمایش داده نمی‌شود. اگر فیلد رمز را خالی بگذارید و نام کاربری را تغییر ندهید، رمز ذخیره‌شده حفظ می‌شود؛ خالی گذاشتن هم‌زمان نام کاربری و رمز عبور، احراز هویت پراکسی بالادستی را پاک می‌کند.

در حالت فعال، کاسپین یک outbound از نوع SOCKS5 برای Xray می‌سازد و outbound تونل انتخاب‌شده را از طریق آن زنجیره می‌کند. مسیر کلی ترافیک همچنان به outbound تونل اشاره می‌کند؛ بنابراین فعال کردن این گزینه به‌تنهایی باعث نمی‌شود ترافیک معمول دستگاه‌ها مستقیماً وارد SOCKS5 بالادستی شود.

در مخزن، یک آزمون End-to-End با یک سرور SOCKS5 داخلی وجود دارد. این آزمون ترافیک واقعی VLESS را در دو حالت بدون احراز هویت و با احراز هویت بررسی می‌کند و مستقیماً تأیید می‌کند که سرور SOCKS5 اتصال به سرور VLESS را دریافت کرده است.

## روش‌های اتصال و قالب‌های پشتیبانی‌شده

برای شروع، مودم یا روتر را با کابل اترنت به کامپیوتر کاسپین وصل کنید. برای هات‌اسپات از وای‌فای داخلی آن کامپیوتر، یا در لینوکس از یک آداپتور USB وای‌فای سازگار استفاده کنید. در این چیدمان، ورودی اینترنت و هات‌اسپات آداپتورهای جدا دارند. این پیشنهاد برای شروع است؛ تضمین سرعت اندازه‌گیری‌شده نیست.

در این شکل‌ها، [1] مودم یا روتر اینترنت، [2] کامپیوتر کاسپین و [3] گوشی یا دستگاه دیگر شماست. ETH یعنی کابل اترنت. آداپتور USB اترنت اینترنت را وارد کامپیوتر می‌کند؛ آداپتور USB وای‌فای اتصال بی‌سیم ایجاد می‌کند. این دو وسیله کار یکسانی ندارند.

<div dir="ltr" align="left">

```text
A  [1] --ETH--> [2] --built-in Wi-Fi--> [3]
B  [1] --ETH--> [2] --USB Wi-Fi-------> [3]
C  [1] --Wi-Fi A--> [2] --Wi-Fi B----> [3]
D  [1] --Wi-Fi--> [2: one radio] --Wi-Fi--> [3]
```

</div>

| ورودی اینترنت کاسپین | هات‌اسپات برای دستگاه‌ها | لینوکس و رزبری‌پای | macOS |
|---|---|---|---|
| A. اترنت | وای‌فای داخلی | اگر درایور بتواند هات‌اسپات بسازد، پشتیبانی می‌شود | چیدمان پشتیبانی‌شده |
| B. اترنت | وای‌فای USB خارجی | درایور لینوکس باید از حالت نقطهٔ دسترسی (AP) پشتیبانی کند | کاسپین آن را به‌عنوان هات‌اسپات پشتیبانی نمی‌کند |
| C. آداپتور وای‌فای A | آداپتور وای‌فای جداگانهٔ B | آداپتور B باید حالت AP داشته باشد | هات‌اسپات روی وای‌فای USB خارجی پشتیبانی نمی‌شود |
| D. وای‌فای | همان رادیوی وای‌فای | مشروط به پشتیبانی هم‌زمان از اتصال به شبکه و AP؛ ممکن است کانال مشترک باشد | روی رادیوی داخلی پشتیبانی نمی‌شود |

این جدول نشان می‌دهد کد فعلی چه چیدمان‌هایی را می‌پذیرد یا رد می‌کند. همهٔ آداپتورها، نسخه‌های سیستم‌عامل و لپ‌تاپ‌ها تأیید نشده‌اند. آداپتوری که به وای‌فای خانه وصل می‌شود، لزوماً نمی‌تواند هات‌اسپات بسازد. چیدمان‌های USB لینوکس آزمون مدل‌شده دارند؛ سابقهٔ آزمون سخت‌افزاری، کارکرد همهٔ آداپتورهای USB را ثابت نمی‌کند. در مک، مسیر مستندشده اترنت به وای‌فای داخلی است. افزودن وای‌فای USB این محدودیت را برطرف نمی‌کند.

کاسپین لینک‌های VLESS، VMess، Shadowsocks، SOCKS، Trojan و Hysteria2، از جمله نام جایگزین hy2 را می‌پذیرد. قالب‌های پشتیبانی‌شدهٔ Clash/Clash.Meta YAML، Xray JSON، فهرست لینک و محتوای اشتراک base64 نیز پذیرفته می‌شوند. از فهرست هر موردی را که انتخاب کنید استفاده می‌شود. نشانی اشتراک را می‌توان کنار کانفیگ ذخیره کرد و با زدن دکمه، از درون تونل تازه کرد. از ارائه‌دهنده خودِ کانفیگ سازگار را بگیرید، نه رمز حساب یا پیوند یک صفحهٔ وب.

نام‌های ترابری شامل raw/tcp، ws، grpc، httpupgrade، xhttp/splithttp و kcp/mkcp هستند. پروتکل، ترابری و تنظیمات امنیت باید سازگار باشند؛ همهٔ ترکیب‌ها کار نمی‌کنند. لینک‌های TUIC، WireGuard، SSR، AnyTLS و Hysteria نسخهٔ 1 پشتیبانی نمی‌شوند. نام پروتکل ناسازگار را برای عبور از اعتبارسنجی عوض نکنید. محدودیت‌ها و شواهد آزمون را در راهنمای پروتکل‌ها بخوانید.

[شکل‌های اتصال، آماده‌سازی کابل پیش از شروع، راه‌اندازی دوبارهٔ سرویس‌ها و خطاهای رایج را در راهنمای عیب‌یابی کاربران خانگی بخوانید.](https://github.com/Iman/caspian/wiki/Troubleshooting.fa)

## نصب و راهنماها

پردازنده و رم: حداقل رم، تعداد هسته و سرعت پردازندهٔ موردنیاز کاسپین هنوز با اندازه‌گیری مشخص نشده است. مصرف منابع به حجم ترافیک، پروتکل پراکسی و تعداد اتصال‌های هم‌زمان بستگی دارد. برای اعلام حداقل نیازمندی‌ها، باید مصرف منابع در حالت بیکار و زیر بار اندازه‌گیری شود.

<div dir="ltr" align="left">

| <span dir="rtl">موضوع</span> | English | فارسی | Русский | 中文 | العربية | اردو | Türkçe |
|---|---|---|---|---|---|---|---|
| <span dir="rtl">شروع کار</span> | [English](https://github.com/Iman/caspian/wiki/Getting-Started) | [فارسی](https://github.com/Iman/caspian/wiki/Getting-Started.fa) | [Русский](https://github.com/Iman/caspian/wiki/Getting-Started.ru) | [中文](https://github.com/Iman/caspian/wiki/Getting-Started.zh) | [العربية](https://github.com/Iman/caspian/wiki/Getting-Started.ar) | [اردو](https://github.com/Iman/caspian/wiki/Getting-Started.ur) | [Türkçe](https://github.com/Iman/caspian/wiki/Getting-Started.tr) |
| <span dir="rtl">نصب</span> | [English](https://github.com/Iman/caspian/wiki/Installation) | [فارسی](https://github.com/Iman/caspian/wiki/Installation.fa) | [Русский](https://github.com/Iman/caspian/wiki/Installation.ru) | [中文](https://github.com/Iman/caspian/wiki/Installation.zh) | [العربية](https://github.com/Iman/caspian/wiki/Installation.ar) | [اردو](https://github.com/Iman/caspian/wiki/Installation.ur) | [Türkçe](https://github.com/Iman/caspian/wiki/Installation.tr) |
| <span dir="rtl">نصب در Linux و Raspberry Pi</span> | [English](https://github.com/Iman/caspian/wiki/Install-Linux) | [فارسی](https://github.com/Iman/caspian/wiki/Install-Linux.fa) | [Русский](https://github.com/Iman/caspian/wiki/Install-Linux.ru) | [中文](https://github.com/Iman/caspian/wiki/Install-Linux.zh) | [العربية](https://github.com/Iman/caspian/wiki/Install-Linux.ar) | [اردو](https://github.com/Iman/caspian/wiki/Install-Linux.ur) | [Türkçe](https://github.com/Iman/caspian/wiki/Install-Linux.tr) |