<<<<<<< HEAD
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
=======
# Instagram to website automation by rakesh



## Getting started

To make it easy for you to get started with GitLab, here's a list of recommended next steps.

Already a pro? Just edit this README.md and make it your own. Want to make it easy? [Use the template at the bottom](#editing-this-readme)!

## Add your files

* [Create](https://docs.gitlab.com/user/project/repository/web_editor/#create-a-file) or [upload](https://docs.gitlab.com/user/project/repository/web_editor/#upload-a-file) files
* [Add files using the command line](https://docs.gitlab.com/topics/git/add_files/#add-files-to-a-git-repository) or push an existing Git repository with the following command:

```
cd existing_repo
git remote add origin https://gitlab.com/darshanddigital/instagram-to-website-automation-by-rakesh.git
git branch -M main
git push -uf origin main
```

## Integrate with your tools

* [Set up project integrations](https://gitlab.com/darshanddigital/instagram-to-website-automation-by-rakesh/-/settings/integrations)

## Collaborate with your team

* [Invite team members and collaborators](https://docs.gitlab.com/user/project/members/)
* [Create a new merge request](https://docs.gitlab.com/user/project/merge_requests/creating_merge_requests/)
* [Automatically close issues from merge requests](https://docs.gitlab.com/user/project/issues/managing_issues/#closing-issues-automatically)
* [Enable merge request approvals](https://docs.gitlab.com/user/project/merge_requests/approvals/)
* [Set auto-merge](https://docs.gitlab.com/user/project/merge_requests/auto_merge/)

## Test and Deploy

Use the built-in continuous integration in GitLab.

* [Get started with GitLab CI/CD](https://docs.gitlab.com/ci/quick_start/)
* [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/user/application_security/sast/)
* [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/topics/autodevops/requirements/)
* [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/user/clusters/agent/)
* [Set up protected environments](https://docs.gitlab.com/ci/environments/protected_environments/)

***

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name
Choose a self-explaining name for your project.

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage
Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support
Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap
If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing
State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
>>>>>>> 34c1fdf0d0dbff9aec1edd3fdeea52ba8b9496ff
