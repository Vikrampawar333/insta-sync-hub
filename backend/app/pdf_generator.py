"""
Pure Python Multi-Page PDF Generator for InstaSync Hub Theory Guide
Zero external dependencies required. Generates standard PDF-1.4.
"""

import os
import textwrap

class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.pages = []  # list of byte streams for each page
        self.current_stream = []
        self.page_width = 595.28
        self.page_height = 841.89
        self.margin_left = 50
        self.margin_right = 50
        self.margin_top = 50
        self.margin_bottom = 55
        self.content_width = self.page_width - self.margin_left - self.margin_right
        self.y = self.page_height - self.margin_top
        self.new_page()

    def new_page(self):
        if self.current_stream:
            self.pages.append(b"".join(self.current_stream))
            self.current_stream = []
        self.y = self.page_height - self.margin_top
        # Page header
        self.draw_header()

    def draw_header(self):
        # Subtle header bar
        stream = f"""
        0.6 0.6 0.6 RG
        0.5 w
        {self.margin_left} {self.page_height - 35} m
        {self.page_width - self.margin_right} {self.page_height - 35} l
        S
        BT
        /F1 8 Tf
        0.5 0.5 0.5 rg
        {self.margin_left} {self.page_height - 30} Td
        (InstaSync Hub - Complete Theory & Architecture Guide) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)

    def draw_footer(self, page_num, total_pages):
        stream = f"""
        0.8 0.8 0.8 RG
        0.5 w
        {self.margin_left} 40 m
        {self.page_width - self.margin_right} 40 l
        S
        BT
        /F1 8 Tf
        0.5 0.5 0.5 rg
        {self.margin_left} 28 Td
        (Confidential - 100% Free Lifetime Architecture) Tj
        ET
        BT
        /F1 8 Tf
        0.5 0.5 0.5 rg
        {self.page_width - self.margin_right - 60} 28 Td
        (Page {page_num} of {total_pages}) Tj
        ET
        """.encode("latin1")
        return stream

    def check_space(self, needed_height):
        if self.y - needed_height < self.margin_bottom:
            self.new_page()

    def escape_text(self, text):
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def add_title(self, text):
        self.check_space(50)
        escaped = self.escape_text(text)
        stream = f"""
        BT
        /F2 18 Tf
        0.06 0.09 0.16 rg
        {self.margin_left} {self.y - 18} Td
        ({escaped}) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)
        self.y -= 26

    def add_subtitle(self, text):
        self.check_space(25)
        escaped = self.escape_text(text)
        stream = f"""
        BT
        /F3 11 Tf
        0.4 0.45 0.55 rg
        {self.margin_left} {self.y - 11} Td
        ({escaped}) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)
        self.y -= 20

    def add_chapter_heading(self, number, title):
        self.check_space(45)
        self.y -= 10
        # Draw accent bar
        stream = f"""
        0.9 0.2 0.4 RG
        2 w
        {self.margin_left} {self.y - 20} m
        {self.page_width - self.margin_right} {self.y - 20} l
        S
        BT
        /F2 13 Tf
        0.06 0.09 0.16 rg
        {self.margin_left} {self.y - 14} Td
        (CHAPTER {number}: {self.escape_text(title.upper())}) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)
        self.y -= 30

    def add_section_heading(self, text):
        self.check_space(28)
        self.y -= 6
        escaped = self.escape_text(text)
        stream = f"""
        BT
        /F2 11 Tf
        0.12 0.16 0.23 rg
        {self.margin_left} {self.y - 11} Td
        ({escaped}) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)
        self.y -= 18

    def add_paragraph(self, text):
        lines = textwrap.wrap(text, width=82)
        needed_height = len(lines) * 14 + 6
        self.check_space(needed_height)

        for line in lines:
            escaped = self.escape_text(line)
            stream = f"""
            BT
            /F1 9.5 Tf
            0.15 0.2 0.28 rg
            {self.margin_left} {self.y - 10} Td
            ({escaped}) Tj
            ET
            """.encode("latin1")
            self.current_stream.append(stream)
            self.y -= 13
        self.y -= 6

    def add_bullet(self, bold_prefix, text):
        full_text = f"- {bold_prefix}: {text}" if bold_prefix else f"- {text}"
        lines = textwrap.wrap(full_text, width=80)
        needed_height = len(lines) * 14 + 4
        self.check_space(needed_height)

        for i, line in enumerate(lines):
            indent = self.margin_left if i == 0 else self.margin_left + 12
            escaped = self.escape_text(line)
            stream = f"""
            BT
            /F1 9.5 Tf
            0.15 0.2 0.28 rg
            {indent} {self.y - 10} Td
            ({escaped}) Tj
            ET
            """.encode("latin1")
            self.current_stream.append(stream)
            self.y -= 13
        self.y -= 4

    def add_code_box(self, code_text):
        lines = code_text.strip().split("\n")
        box_height = len(lines) * 13 + 14
        self.check_space(box_height + 10)

        # Background box
        stream = f"""
        0.96 0.97 0.98 rg
        {self.margin_left} {self.y - box_height} {self.content_width} {box_height} re
        f
        0.85 0.88 0.92 RG
        0.5 w
        {self.margin_left} {self.y - box_height} {self.content_width} {box_height} re
        S
        """.encode("latin1")
        self.current_stream.append(stream)

        line_y = self.y - 14
        for line in lines:
            escaped = self.escape_text(line[:78])
            code_stream = f"""
            BT
            /F4 8.5 Tf
            0.1 0.2 0.35 rg
            {self.margin_left + 10} {line_y} Td
            ({escaped}) Tj
            ET
            """.encode("latin1")
            self.current_stream.append(code_stream)
            line_y -= 13

        self.y -= (box_height + 10)

    def add_highlight_box(self, title, text):
        lines = textwrap.wrap(text, width=76)
        box_height = len(lines) * 13 + 28
        self.check_space(box_height + 10)

        # Draw green tinted box
        stream = f"""
        0.94 0.98 0.95 rg
        {self.margin_left} {self.y - box_height} {self.content_width} {box_height} re
        f
        0.1 0.6 0.3 RG
        2 w
        {self.margin_left} {self.y} m
        {self.margin_left} {self.y - box_height} l
        S
        BT
        /F2 9.5 Tf
        0.08 0.45 0.2 rg
        {self.margin_left + 10} {self.y - 14} Td
        ({self.escape_text(title)}) Tj
        ET
        """.encode("latin1")
        self.current_stream.append(stream)

        text_y = self.y - 28
        for line in lines:
            escaped = self.escape_text(line)
            p_stream = f"""
            BT
            /F1 9 Tf
            0.15 0.3 0.2 rg
            {self.margin_left + 10} {text_y} Td
            ({escaped}) Tj
            ET
            """.encode("latin1")
            self.current_stream.append(p_stream)
            text_y -= 13

        self.y -= (box_height + 10)

    def build(self):
        # Finalize last page
        if self.current_stream:
            self.pages.append(b"".join(self.current_stream))

        total_pages = len(self.pages)
        # Add footers to all pages
        finalized_pages = []
        for i, page_bytes in enumerate(self.pages, 1):
            footer = self.draw_footer(i, total_pages)
            finalized_pages.append(page_bytes + footer)

        # PDF Object assembly
        objects = []

        # Object 1: Catalog
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")

        # Object 2: Pages root
        kids = " ".join([f"{3 + i * 2} 0 R" for i in range(total_pages)])
        objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {total_pages} >>".encode("latin1"))

        # Add page objects & content streams
        for i in range(total_pages):
            page_obj_idx = 3 + i * 2
            content_obj_idx = 4 + i * 2

            page_dict = f"""<<
                /Type /Page
                /Parent 2 0 R
                /MediaBox [0 0 {self.page_width} {self.page_height}]
                /Contents {content_obj_idx} 0 R
                /Resources <<
                    /Font <<
                        /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>
                        /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>
                        /F3 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>
                        /F4 << /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>
                    >>
                >>
            >>""".encode("latin1")
            objects.append(page_dict)

            content_data = finalized_pages[i]
            stream_obj = f"<< /Length {len(content_data)} >>\nstream\n".encode("latin1") + content_data + b"\nendstream"
            objects.append(stream_obj)

        # Output generation with xref
        output = [b"%PDF-1.4\n"]
        xref_offsets = [0]

        for i, obj_data in enumerate(objects, 1):
            offset = sum(len(part) for part in output)
            xref_offsets.append(offset)
            output.append(f"{i} 0 obj\n".encode("latin1"))
            output.append(obj_data)
            output.append(b"\nendobj\n")

        xref_start = sum(len(part) for part in output)
        output.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin1"))

        for off in xref_offsets[1:]:
            output.append(f"{off:010d} 00000 n \n".encode("latin1"))

        output.append(f"""trailer
<<
  /Size {len(objects) + 1}
  /Root 1 0 R
>>
startxref
{xref_start}
%%EOF
""".encode("latin1"))

        with open(self.filename, "wb") as f:
            f.write(b"".join(output))

        return self.filename


def generate_insta_theory_pdf(output_path):
    pdf = PDFGenerator(output_path)

    # Cover Title
    pdf.add_title("InstaSync Hub - Complete Theory & Architecture Guide")
    pdf.add_subtitle("100% Free Lifetime | Real-Time Instagram Live Feed Engine | Complete SOP Manual")
    pdf.add_highlight_box(
        "KEY PRODUCT VALUE",
        "This system connects directly to Meta Graph API, stores media permanently on local server disk, and automatically updates any client website without monthly fees or page refresh."
    )

    # Chapter 1
    pdf.add_chapter_heading(1, "Project Ka Introduction & Background")
    pdf.add_section_heading("1.1 Market Me Problem Kya Thi?")
    pdf.add_paragraph(
        "Aaj har business (jaise Gym, Restaurant, Jeweller, Doctor, Fashion Boutique) chahta hai ki unke Instagram ke naye photos aur video reels unki official website par automatic live dikhein."
    )
    pdf.add_paragraph(
        "Lekin market ke third-party plugins (jaise Elfsight, Tagembed, Smash Balloon) har website ke liye Rs.1,000 se Rs.3,500 ($15 to $50) har mahine charge karte hain. Agar agency ke paas 10 clients hain, toh saal ka Rs.1,50,000 se Rs.3,00,000 sirf ek widget ke liye kharch hota hai."
    )
    pdf.add_section_heading("1.2 Hamara Solution")
    pdf.add_paragraph(
        "Humne ek aisa in-house engine banaya hai jo directly official Meta Graph API se connect karta hai. Yeh photos aur reels ko apne server par download karke save kar leta hai aur kisi bhi website par bina kisi monthly charge ke lifetime free feed dikhata hai."
    )

    # Chapter 2
    pdf.add_chapter_heading(2, "Meta Graph API Ki Poori Theory")
    pdf.add_section_heading("2.1 API (Application Programming Interface)")
    pdf.add_paragraph(
        "API ek aisi digital khidki hoti hai jiske zariye do alag softwares aapas me baat karte hain. Hamara Python backend Instagram ke server se data mangwata hai aur Instagram JSON format me data bhejta hai."
    )
    pdf.add_section_heading("2.2 Personal vs Professional Account")
    pdf.add_bullet("Personal Account", "Normal users ke liye hota hai. Meta ispe Graph API access nahi deta.")
    pdf.add_bullet("Professional / Business Account", "Businesses ke liye hota hai. Yeh Instagram app me 1 minute me free switch ho jata hai aur ispe Meta full Graph API access deta hai.")
    pdf.add_bullet("Facebook Page Linking", "Instagram Business account ka ek Facebook Page se link hona zaroori hota hai taaki Graph API token generate ho sake.")
    pdf.add_section_heading("2.3 Access Token & Auto-Refresh")
    pdf.add_paragraph(
        "Access Token ek Digital Password ki tarah hota hai. Short-lived token 1-2 ghante ka hota hai, jabki Long-lived token 60 Din tak valid rehta hai."
    )
    pdf.add_paragraph(
        "Meta ek official refresh API deta hai: https://graph.instagram.com/refresh_access_token. Hamara backend har 30-45 din me is token ko background me automatically renew kar deta hai, isliye yeh token Lifetime Unlimited chalta rehta hai jab tak user password change na kare."
    )

    # Chapter 3
    pdf.add_chapter_heading(3, "Media Storage Engine (CDN Expiry Problem)")
    pdf.add_section_heading("3.1 Instagram CDN Links 3 Din Me Expire Kyu Hote Hain?")
    pdf.add_paragraph(
        "Instagram ke photos aur videos ka link Meta ke servers (fbcdn.net) se aata hai. Meta ki strict security policy hai ki yeh image links 3 din (72 ghante) baad expire ho jate hain."
    )
    pdf.add_paragraph(
        "Agar hum Instagram ka direct link website par lagate, toh 3 din baad client ki website par saari photos gayab ho jati aur broken image ka icon aa jata."
    )
    pdf.add_section_heading("3.2 Hamara Permanent Local Storage Solution")
    pdf.add_bullet("Streaming Download", "Jab bhi naya post detect hota hai, backend photo (.jpg) ya video reel (.mp4) ko turant server ki hard drive (backend/media/) par download kar leta hai.")
    pdf.add_bullet("Local URL Mapping", "Database me Instagram ke expiring link ki jagah local path (jaise /media/18102065894198422.jpg) save ho jata hai.")
    pdf.add_bullet("Lifetime Validity", "Client ki website hamare local server se media load karti hai, isliye photos hamesha ke liye safe rehti hain.")

    # Chapter 4
    pdf.add_chapter_heading(4, "Real-Time Auto Sync Engine")
    pdf.add_section_heading("4.1 Bina Refresh Ke Live Kaise Aata Hai?")
    pdf.add_paragraph(
        "FastAPI server ke andar ek asynchronous background task (periodic_instagram_sync) chalta hai jo har 15 second me Meta Graph API se latest media IDs check karta hai."
    )
    pdf.add_section_heading("4.2 Automatic Add & Delete Logic")
    pdf.add_bullet("Auto Add", "Naya post milne par photo download hoti hai aur database me save ho jati hai.")
    pdf.add_bullet("Auto Delete", "Agar client ne Instagram se post delete kiya, toh backend local database se bhi use delete kar deta hai: DELETE FROM instagram_posts WHERE ig_media_id NOT IN (...).")
    pdf.add_bullet("SSE Signal (Server-Sent Events)", "Post add ya delete hote hi server browser ko sync_completed ka signal bhejta hai. Browser ka widget bina page reload kiye screen par post ko smoothly update kar deta hai.")

    # Chapter 5
    pdf.add_chapter_heading(5, "Database Architecture (SQLite WAL Mode)")
    pdf.add_section_heading("5.1 SQLite Kyu Chuna?")
    pdf.add_paragraph(
        "SQLite ek Single-File Database (insta_hub.db) hai. Iske liye koi alag MySQL server install nahi karna padta. Poora database ek hi file me hota hai, isliye yeh super portable aur ultra-fast hai (response time under 5ms)."
    )
    pdf.add_section_heading("5.2 WAL Mode (Write-Ahead Logging)")
    pdf.add_paragraph(
        "Normal SQLite me ek time par ek process likh sakta hai aur doosra wait karta hai (Database Lock). Humne database me WAL mode enable kiya hai (PRAGMA journal_mode=WAL; PRAGMA busy_timeout=30000;). Isse background sync naye posts likhta rehta hai aur hazaron visitors bina kisi rukawat ke website par feed dekhte rehte hain."
    )

    # Chapter 6
    pdf.add_chapter_heading(6, "Universal Frontend Widget Embedding")
    pdf.add_section_heading("6.1 Lightweight Script vs iFrame")
    pdf.add_paragraph(
        "Puraane zamane ke widgets iFrame me chalte the jo mobile par slow hote hain. Hamara widget Pure Vanilla JS aur Vanilla CSS me bana hai (Size sirf 8 KB). Isme zero external dependencies hain (no React, no jQuery)."
    )
    pdf.add_section_heading("6.2 Authentic 3-Column Card Layout")
    pdf.add_paragraph(
        "Card ka design authentic Instagram embed format me hai: Profile Avatar, Username, View Profile button, 1:1 Square Media, View More on Instagram link, Action Icons (Heart, Comment, Share, Save), Real Likes count, aur caption toggle."
    )

    # Chapter 7
    pdf.add_chapter_heading(7, "Client Onboarding SOP (Step-by-Step)")
    pdf.add_section_heading("Jab Bhi Kisi Client Ka Order Aaye:")
    pdf.add_bullet("Step 1", "Client se confirm karein ki unka Instagram account Professional/Business hai aur Facebook Page se link hai.")
    pdf.add_bullet("Step 2", "developers.facebook.com/tools/explorer par jakar client ka Facebook Page select karke Long-Lived Token aur INSTAGRAM_ACCOUNT_ID generate karein.")
    pdf.add_bullet("Step 3", "Server ke backend/.env file me client ka ID aur Token paste karein.")
    pdf.add_bullet("Step 4", "Client ki website par Embed Code paste karein:")
    pdf.add_code_box("""<!-- Container -->
<div id="insta-feed-widget"></div>

<!-- CSS & JS -->
<link rel="stylesheet" href="https://your-server.com/widget/insta-feed.css">
<script src="https://your-server.com/widget/insta-feed.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', () => {
    InstaHub.init({
      container: '#insta-feed-widget',
      apiUrl: 'https://your-server.com'
    });
  });
</script>""")

    # Chapter 8
    pdf.add_chapter_heading(8, "Hosting & Business Earning Models")
    pdf.add_section_heading("8.1 Self-Hosted Model (Client ke Server par)")
    pdf.add_paragraph(
        "Client ke hi hosting ya VPS par backend daal dein. Client se One-Time Setup Fee lein (jaise Rs.3,000 se Rs.8,000). Aapka recurring kharcha zero rahega."
    )
    pdf.add_section_heading("8.2 Agency SaaS Model (Central Cloud Server par)")
    pdf.add_paragraph(
        "Ek saste cloud server (jaise Render ya $4/mo DigitalOcean) par apna backend chalayein aur sabhi clients ko API link dein. Client se Monthly ya Yearly Recurring Subscription lein (jaise Rs.499/month ya Rs.3,500/year per client)."
    )

    pdf.build()
    return output_path

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "InstaSync_Hub_Theory_Guide.pdf")
    generate_insta_theory_pdf(out)
    print("PDF generated successfully:", out)
