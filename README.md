# 🚀 InstaSync Hub — Real-Time Instagram & Community Platform

> **100% Free Lifetime Architecture | Zero Subscriptions | Universal Website Plug & Play**

InstaSync Hub ek enterprise-grade full-stack solution hai jo **Instagram Posts aur Reels ko real-time mein aapki website par automatically sync karta hai**, aur sath hi aapki website ke liye ek **separate social community feed** bhi provide karta hai.

---

## 📋 Features Checklist (Company Requirements)

| Requirement | Supported | Implementation Detail |
| :--- | :---: | :--- |
| **1. Instagram Post website par lana** | ✅ | Meta Graph API + SQLite Caching + Local Disk Storage |
| **2. Instagram Reel website par lana** | ✅ | Native Video Player support with Reels 9:16 layout & thumbnail preview |
| **3. Caption show karna** | ✅ | Caption formatting with line clamps and full view modal |
| **4. Comments read karna** | ✅ | Complete comment thread listing with usernames & timestamps |
| **5. Instagram comments ka reply** | ✅ | Direct reply to comments via `POST /{comment-id}/replies` Graph API |
| **6. Website se Post like/unlike** | ✅ | Optimistic UI heart animation + SQLite website likes tracker |
| **7. Website se Comment like** | ✅ | Comment moderation & engagement tracking |
| **8. Profile/Business information** | ✅ | Real-time follower count, bio, profile image & media count |
| **9. Website par apna separate feed** | ✅ | **Dedicated Community Feed** jahan website visitors direct post & interact kar sakte hain |
| **10. Real-time Live Sync (Instant)** | ✅ | **Meta Webhooks + Server-Sent Events (SSE)** — Bina page refresh kiye instant update |

---

## 💰 100% Free Lifetime — Kyu Kabhi Pay Nahi Karna Padega?

1. **Meta Graph API:** Meta official API bilkul **FREE** hai. Iske liye koi subscription nahi hoti.
2. **Database:** Built-in **SQLite** (`insta_hub.db`) use karta hai. Isme koi paid cloud database (Supabase/MongoDB paid plan) nahi chahiye.
3. **Media Storage:** Instagram ke CDN links 3 din baad expire ho jate hain. Hamara server media ko unke server ke `media/` folder mein **locally download** karke serve karta hai. Zero AWS S3 or Cloudinary cost!
4. **Real-Time Push:** WebSockets ya third-party paid push services (Pusher, Firebase) ke bajaye HTTP standard **Server-Sent Events (SSE)** use hota hai jo 100% free hai.
5. **Existing Hosting:** Aapki company ke paas already domain aur hosting hai, toh yeh backend unhi ke server par chalega — **₹0 extra cost**.

---

## 🛠️ Quick Start (Local Run & Testing)

### 1. Requirements Install Karein
```bash
cd backend
pip install -r requirements.txt
```

### 2. Server Start Karein
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Open Browser
Visit: [http://localhost:8000](http://localhost:8000)

Aapko complete live interface dikhega:
- **Instant Simulator Button**: Top bar par *"Simulate Instant Instagram Upload"* button dabayein aur dekhein kaise bina page reload kiye naya Instagram post website par real-time alert ke saath load hota hai!

---

## 🔌 Company Ki Existing Website Mein Kaise Add Karein?

Yeh widget **universal** hai. Unki website chahe **PHP, WordPress, React, Laravel, ya HTML** par ho, sirf yeh 2 steps follow karne hain:

### Step 1: HTML Element Add Karein
Jahan bhi feed dikhana ho, wahan yeh `div` paste karein:
```html
<div id="company-insta-hub"></div>
```

### Step 2: Script aur CSS Link Karein
Website ke header ya footer mein yeh 3 lines paste karein:
```html
<!-- Stylesheet -->
<link rel="stylesheet" href="https://your-domain.com/widget/insta-feed.css">

<!-- JavaScript Widget -->
<script src="https://your-domain.com/widget/insta-feed.js"></script>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    InstaHub.init({
      container: '#company-insta-hub',
      apiUrl: 'https://your-domain.com', // FastAPI Backend ka URL
      theme: 'dark' // ya 'light'
    });
  });
</script>
```

---

## 🔑 Meta Developer Account Setup (100% Free Step-by-Step)

1. **Meta Developers Portal**: [developers.facebook.com](https://developers.facebook.com) par free login karein.
2. **Create App**: App Type **"Business"** select karein.
3. **Products Add Karein**:
   - **Instagram Graph API**
   - **Webhooks**
4. **Development Mode**: App ko Development Mode mein hi rakhein. Apne company ke Instagram account ko **App Roles -> Testers** mein add karein (Isse koi App Review ya verification fee nahi lagti).
5. **Get Token**: Graph API Explorer se 60-day **Long-Lived Access Token** generate karein aur `backend/.env` file mein daal dein.
6. **Webhook Configure Karein**:
   - Callback URL: `https://your-domain.com/api/webhook`
   - Verify Token: `insta_hub_secret_verify_token_2026`
   - Subscribe Fields: `media`, `comments`

---

## 📁 Project Architecture

```
insta-sync-hub/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI server, SSE stream, CORS & routes
│   │   ├── config.py            # Environment settings & credentials
│   │   ├── database.py          # SQLite zero-cost database layer
│   │   ├── models.py            # Pydantic schemas
│   │   ├── instagram_service.py # Graph API sync, local media downloader
│   │   └── webhook_handler.py   # Meta webhook challenge handshake & event listener
│   ├── media/                   # Local server storage for posts & reels
│   ├── requirements.txt         # Dependencies
│   └── .env                     # Configuration keys
│
└── frontend/
    ├── index.html               # Master demo & interactive test page
    ├── insta-feed.js            # Universal pluggable JavaScript widget
    └── insta-feed.css           # Modern dark/light responsive styles
```
