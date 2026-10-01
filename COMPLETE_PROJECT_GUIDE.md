# 📘 InstaSync Hub — Complete Project Guide & Manual
> **100% Free Lifetime • Real-Time Instagram Sync • Universal Embeddable Widget**

---

## 📑 Table of Contents
1. [Project Overview & Purpose](#1-project-overview--purpose)
2. [Complete System Architecture](#2-complete-system-architecture)
3. [Folder & File Directory Breakdown](#3-folder--file-directory-breakdown)
4. [Why It is 100% Free Lifetime (₹0 Cost)](#4-why-it-is-100-free-lifetime-0-cost)
5. [How Real-Time Auto Sync Works (Add & Delete)](#5-how-real-time-auto-sync-works-add--delete)
6. [How to Onboard a New Client (Step-by-Step SOP)](#6-how-to-onboard-a-new-client-step-by-step-sop)
7. [How to Embed on Any Website (WordPress, PHP, Shopify, HTML)](#7-how-to-embed-on-any-website)
8. [Hosting & Deployment Models](#8-hosting--deployment-models)
9. [Important FAQs & Technical Questions](#9-important-faqs--technical-questions)

---

## 1. Project Overview & Purpose

**InstaSync Hub** ek self-contained Instagram live feed and reels engine hai jo market ke mehnge plugins (jaise *Elfsight*, *Tagembed*, *Smash Balloon*) ko replace karta hai. 

Wo plugins har website ke liye **₹1,000 se ₹3,500 ($15–$50) har mahine** lete hain. Yeh system direct Meta (Instagram / Facebook) ke official Graph API se connect karta hai aur **lifetime ₹0** kharche me chalta hai.

### ✨ Key Capabilities:
- **100% Real Instagram Data**: Real photos, real reels, real captions, real likes, real avatars. (Koi bhi fake tick, fake likes ya dummy text nahi hai).
- **Auto-Sync without Page Refresh**: Jab bhi Instagram par naya post upload ho ya purana delete ho, website par bina refresh kiye turant update ho jata hai.
- **Permanent Local Media Storage**: Instagram ke image links 3 din me expire ho jate hain; hamara backend media ko apne server par download karke serve karta hai taaki link kabhi na toote.
- **Authentic 3-Column Card Layout**: Official Instagram embed card layout (`mohanjoshi.in` style).
- **Universal Compatibility**: WordPress, PHP, HTML, Shopify, React, Next.js sabhi me 2 lines of code se embed ho jata hai.

---

## 2. Complete System Architecture

System do parts me divided hai:

```
[ Instagram Account (@vpdem_o) ]
               │
               ▼ (Meta Graph API - Free)
     [ FastAPI Backend Server ]
         │                │
         ▼                ▼
   [ SQLite DB ]    [ Local Media Storage ]
 (insta_hub.db)       (/backend/media/)
         │
         ▼ (SSE Stream + REST API)
  [ Any Website (WordPress / PHP / HTML) ]
 (insta-feed.js + insta-feed.css Widget)
```

| Component | Technology | Role & Functionality |
| :--- | :--- | :--- |
| **Backend Engine** | Python 3.10+ (FastAPI + Uvicorn) | Background sync worker, API endpoints, token handling. |
| **Database** | SQLite (WAL Mode) | `insta_hub.db` file — zero setup, ultra-fast responses (<10ms). |
| **Media Cache** | Local Disk Storage (`/media/`) | High-res `.jpg` aur `.mp4` permanent disk storage. |
| **Realtime Stream**| Server-Sent Events (SSE) | Live push broadcast browser client ko bina refresh update karne ke liye. |
| **Frontend Widget**| Pure Vanilla JS & CSS | Zero external dependencies, pure lightweight widget. |

---

## 3. Folder & File Directory Breakdown

Aapke project ka har ek file kya karta hai:

```text
insta-sync-hub/
├── backend/
│   ├── app/
│   │   ├── main.py              # Main FastAPI app, routes aur background sync worker
│   │   ├── instagram_service.py # Meta API se data fetch karne aur media download karne ka logic
│   │   ├── database.py          # SQLite schema, tables aur WAL mode connection
│   │   ├── config.py            # .env file load karne ki settings
│   │   ├── models.py            # Pydantic schemas (data validation)
│   │   └── webhook_handler.py   # Meta Real-time Webhook router
│   ├── .env                     # Secret Instagram Token aur Account ID
│   ├── .env.example             # New client ke liye reference template
│   ├── insta_hub.db             # Single-file SQLite database (saare posts aur profile saved hain)
│   ├── media/                   # Downloaded photos (.jpg) aur reels (.mp4)
│   └── requirements.txt         # Python libraries (fastapi, uvicorn, httpx, aiofiles)
│
├── frontend/
│   ├── index.html               # Live preview showcase page
│   ├── insta-feed.js            # Embeddable widget script
│   └── insta-feed.css           # Authentic 3-column Instagram card CSS
│
├── PROJECT_MANUAL.html          # PDF-ready printable manual (Ctrl+P -> Save as PDF)
└── COMPLETE_PROJECT_GUIDE.md    # Complete master manual (this file)
```

---

## 4. Why It is 100% Free Lifetime (₹0 Cost)

1. **Meta Graph API is Free**: Meta Instagram Business/Creator accounts ko standard API access **100% free** deta hai (200 requests/user/hour).
2. **Local Caching**: Har visitor jab website kholega, toh server Instagram ko call nahi karega, balki local SQLite database se padhega. Isse Instagram ki API limits kabhi khatam nahi hoti.
3. **Local Media Storage**: Instagram CDN links 3 din me expire ho jate hain. Hamara backend photos/videos ko apne disk par save kar leta hai, isliye koi expensive third-party storage ya CDN nahi chahiye.

---

## 5. How Real-Time Auto Sync Works (Add & Delete)

1. **15-Second Background Check**: Server me `periodic_instagram_sync` har 15 second me Instagram se latest post IDs check karta hai.
2. **New Post Added**: Agar naya post milta hai, server photo/video download karta hai aur database me insert karta hai.
3. **Post Deleted on Instagram**: Agar koi post Instagram se delete ho gaya, server query run karta hai:
   `DELETE FROM instagram_posts WHERE ig_media_id NOT IN (...)` aur use local database se bhi delete kar deta hai.
4. **SSE Event Broadcast**: Server browser ko `sync_completed` event bhejta hai. Browser ka widget bina refresh kiye naye posts ko show kar deta hai aur delete huye posts ko hata deta hai.

---

## 6. How to Onboard a New Client (Step-by-Step SOP)

Jab bhi naya client aaye, bas yeh 4 steps follow karein:

### Step 1: Client se 2 Cheezein Confirm Karein
- Client ka Instagram account **Professional / Business** account hona chahiye (Instagram App me *Settings > Switch to Professional Account* - Free hota hai).
- Instagram account unke **Facebook Page** se connect hona chahiye.

### Step 2: Client ka Token aur ID Generate Karein
1. [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer) par jayein.
2. Client ka Facebook Page select karein aur permissions check karein:
   - `instagram_basic`
   - `pages_show_list`
   - `pages_read_engagement`
3. **Generate Access Token** click karein aur use **60-day Long-Lived Token** me extend kar lein.
4. Query run karein: `GET me/accounts?fields=instagram_business_account`
   - Yahan se `INSTAGRAM_ACCOUNT_ID` mil jayega.

### Step 3: `backend/.env` Update Karein
Client ke credentials paste karein:
```env
INSTAGRAM_ACCOUNT_ID=client_ka_instagram_id
INSTAGRAM_ACCESS_TOKEN=client_ka_access_token
```

### Step 4: Server Run Karein
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Server client ke saare photos aur reels automatically download karke ready kar dega.

---

## 7. How to Embed on Any Website

Client ki website par feed dikhane ke liye sirf yeh 2 code blocks lagane hain:

### A. Jahan feed dikhana hai wahan Container lagayein:
```html
<div id="insta-feed-widget"></div>
```

### B. Page ke Footer ya Header me Script & CSS lagayein:
```html
<!-- Stylesheet -->
<link rel="stylesheet" href="https://your-server-domain.com/widget/insta-feed.css">

<!-- Script -->
<script src="https://your-server-domain.com/widget/insta-feed.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    InstaHub.init({
      container: '#insta-feed-widget',
      apiUrl: 'https://your-server-domain.com' // Aapke server ka live URL
    });
  });
</script>
```

#### Platform Specific Tips:
- **WordPress**: Gutenberg ya Elementor me "Custom HTML" block lein aur yeh code paste kar dein.
- **Shopify**: Theme customize me "Custom Liquid" section add karein aur paste karein.
- **PHP / HTML**: Direct HTML file me jahan feed chahiye wahan paste karein.

---

## 8. Hosting & Deployment Models

| Model | Setup | Best For |
| :--- | :--- | :--- |
| **Model 1: Client ke Server par (Self-Hosted)** | Client ke VPS ya cPanel (Python App) par poora folder daal dein. | Zero cost for you, client ka private server. |
| **Model 2: Central Cloud Server (SaaS)** | Ek central server (Render.com, Railway, ya DigitalOcean) par backend host karein. | Ek hi server se 50+ clients ko manage karna. |
| **Model 3: Localhost** | Apne PC par `http://localhost:8080`. | Development aur client demo ke liye. |

---

## 9. Important FAQs & Technical Questions

### Q1: Kya token expire hota hai?
- Meta ka Long-Lived Token 60 din ka hota hai.
- Meta auto-refresh API provide karta hai (`https://graph.instagram.com/refresh_access_token`), jisse har 30–45 din me yeh token automatically extend ho jata hai.
- Yeh hamesha unlimited chalta rahega jab tak user password change na kare.

### Q2: Database kahan hai?
- Database `backend/insta_hub.db` me SQLite ke roop me saved hai.
- Isko dekhne ke liye VS Code me **SQLite Viewer** extension install karke file par click karein.

### Q3: Agar Instagram down ho gaya toh kya website tutegi?
- **Nahi!** Kyunki saara data aur photos aapke apne local disk aur database me saved hain, isliye website 100% normal fast load hoti rahegi.

---
*InstaSync Hub — Built for High Performance, Zero Monthly Cost & Professional Client Delivery.*
