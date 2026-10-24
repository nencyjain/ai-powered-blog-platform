# AI-Powered Blog Platform ✍️🤖

**A Full-Stack Web Application for 45-Day Industrial Training Project at Codec Technologies**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-API-purple.svg)](https://platform.openai.com/)
[![Storage](https://img.shields.io/badge/Storage-JSON-orange.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

---

## 📌 Project Overview

The **AI-Powered Blog Platform** is a modern, beginner-friendly content management and generation application developed as part of a 45-day industrial training program at **Codec Technologies**. 

The platform allows users to:
1. Generate structured, engaging blog articles using the **OpenAI API** (or the zero-cost **Demo Mode** when no API key is present).
2. Edit content in an interactive editor with a live **Markdown-to-HTML** preview.
3. Optimize articles for search engines using an **AI SEO Assistant** that creates meta titles, meta descriptions, and keywords.
4. Manage blog posts with **Draft** and **Published** statuses.
5. Store articles in a lightweight, persistent JSON database (`data/blogs.json`).

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Python Flask | Lightweight web server and REST API endpoints |
| **Frontend** | HTML5, CSS3, JavaScript | Modern, responsive UI with zero external heavy frameworks |
| **AI Integration** | OpenAI API (`gpt-4o-mini`) | Structured article and SEO metadata generation |
| **Fallback Engine** | Built-in Demo Generator | Full functionality without requiring an OpenAI API key |
| **Database** | JSON Storage (`data/blogs.json`) | File-based data persistence (easy to inspect and back up) |
| **Version Control** | Git & GitHub | Complete `.gitignore` and clean repository structure |

---

## ✨ Key Features

### 1. Modern Dashboard
- Clean, responsive dashboard with metrics: **Total Posts**, **Published Posts**, and **Drafts**.
- Instant search bar to filter posts by title or topic.
- Tab filters: *All Posts*, *Published*, and *Drafts*.
- Quick action buttons to **View**, **Edit**, or **Delete** posts.

### 2. AI Blog Generator
- Configurable generation parameters:
  - **Topic:** Any idea or subject.
  - **Tone:** Professional, Friendly, Educational, or Casual.
  - **Length:** Short (~350 words), Medium (~650 words), or Long (~1000 words).
- Generates structured markdown including Title, Intro, Headings (`##`, `###`), Lists, Blockquotes, Code snippets, and Conclusion.
- Clear error messages if the API key is missing or quota is exceeded.

### 3. Interactive Markdown Editor
- Real-time side-by-side **Markdown preview**.
- Formatting toolbar for bold, italic, headings, quotes, lists, and code blocks.
- View modes: **Split View** (side-by-side), **Write** (editor only), and **Preview** (rendered HTML only).
- Live word count and estimated reading time.

### 4. SEO Assistant
- Generates optimized:
  - **SEO Meta Title** (character counter with 60-character target indicator).
  - **Meta Description** (character counter with 160-character indicator).
  - **Target Keywords** (comma-separated).
- Live **Google Search Result Snippet Preview** to visualize how the post will appear on search engines.

### 5. Demo Mode (Zero-Key Testing)
- Works 100% out of the box even without an OpenAI account or API key.
- Clearly labeled with **Demo Mode** badges so students never falsely claim real AI generation when keys are absent.
- Provides realistic, high-quality sample blog and SEO generations.

### 6. Public Reader View
- Accessible at `/blog/<id>`.
- Injects generated SEO tags (`<meta name="description">`, `<meta name="keywords">`, `<meta property="og:title">`) directly into the HTML `<head>`.
- Formatted reading view with reading time and author credentials.

---

## 📁 Project Directory Structure

```text
ai-powered-blog-platform/
│
├── app.py                 # Core Flask application: routes, APIs, JSON helpers, AI handlers
├── requirements.txt       # Python package dependencies
├── .env.example           # Example environment variables template
├── .gitignore             # Git ignore file for secrets (.env) and Python cache
├── README.md              # Complete project documentation
│
├── data/
│   └── blogs.json         # JSON database storing blog articles
│
├── static/
│   ├── style.css          # Modern CSS stylesheet (blue/purple accents, responsive)
│   └── script.js          # Client-side JavaScript (Markdown preview, AI calls, DOM)
│
└── templates/
    ├── index.html         # Dashboard template (metrics, blog cards, filters)
    ├── editor.html        # Blog editor and AI generation template
    └── blog.html          # Public reader view template with SEO meta tags
```

---

## 🚀 Setup & Installation (Windows)

Follow these exact steps to run the application on your Windows computer:

### Step 1: Open Terminal in the Project Directory
Open **PowerShell** or **Command Prompt** and navigate to the project directory:
```powershell
cd c:\Users\nency\Downloads\ai-powered-blog-platform
```

### Step 2: (Recommended) Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If running Command Prompt instead of PowerShell, use `.\venv\Scripts\activate.bat`)*

### Step 3: Install Required Packages
```powershell
pip install -r requirements.txt
```

> **Note:** The application includes a fallback design. If `openai` or `python-dotenv` are not yet installed, Flask alone is enough to run the core application and Demo Mode immediately!

### Step 4: Configure OpenAI API Key (Optional)
To use live OpenAI generation instead of Demo Mode:
1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```
3. If you leave `.env` empty or omit it, the application will automatically run in **Demo Mode**.

### Step 5: Start the Flask Application
```powershell
python app.py
```

### Step 6: Open in Your Web Browser
Open your browser and visit:
👉 **http://127.0.0.1:5000**

---

## 🔄 Project Workflow

```text
+-----------------------------------------------------------------+
|                        1. User Dashboard                        |
|   - View total posts, published vs draft counters               |
|   - Search and filter existing posts                            |
|   - Click "Create New Blog"                                     |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                    2. AI Generator / Editor                     |
|   - Enter Topic, select Tone (Educational/Professional)         |
|   - Select Length (Short/Medium/Long)                           |
|   - Click "Generate Blog"                                       |
+-----------------------------------------------------------------+
                                |
                +---------------+---------------+
                |                               |
                v                               v
    [No API Key / Demo Mode]        [OpenAI API Key Provided]
    Generates structured            Calls gpt-4o-mini via
    sample blog & SEO data          OpenAI Chat Completions
                |                               |
                +---------------+---------------+
                                |
                                v
+-----------------------------------------------------------------+
|                    3. Interactive Editing                       |
|   - Edit Title & Content with live Markdown preview             |
|   - Generate / Review SEO title, description, and keywords      |
|   - Inspect Google Search Result snippet simulation             |
+-----------------------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------+
|                    4. Save & Persistence                        |
|   - Click "Save as Draft" or "Publish Post"                     |
|   - Stored persistently in data/blogs.json                      |
|   - View live formatted post at /blog/<slug-id>                 |
+-----------------------------------------------------------------+
```

---

## 🔒 Security Best Practices Implemented

- **Environment Isolation:** API keys are never written in source code or sent to frontend JavaScript.
- **Input Sanitization:** User inputs are escaped before rendering to prevent Cross-Site Scripting (XSS).
- **Safe JSON Storage:** Atomic file operations protect `data/blogs.json` from corruption.
- **Git Protection:** `.env` is listed in `.gitignore` to prevent accidental credential leakage to GitHub.

---

## 🎓 College Viva / Assessment Q&A

Here are common questions examiners ask about this project and the answers:

1. **Q: Why use JSON instead of SQLite or MySQL initially?**
   *A:* JSON storage is lightweight, requires no database server setup, is human-readable, and allows easy inspection of saved posts during training demonstration. The application is modularized so SQLite/PostgreSQL can be swapped in later.
2. **Q: How does the Demo Mode work?**
   *A:* When the backend detects that `OPENAI_API_KEY` is missing or invalid, it routes generation requests to `generate_demo_blog()`, which builds realistic structured markdown posts based on the selected topic, tone, and length without making any external API calls.
3. **Q: How is Markdown converted to HTML without extra heavy packages?**
   *A:* `render_markdown_to_html()` in `app.py` uses Python's `html.escape` to sanitize inputs and regular expressions to convert markdown syntax (`#`, `**`, `*`, ````code````) into secure semantic HTML. The client also features an identical live parser in `script.js`.
4. **Q: How are SEO tags used?**
   *A:* The generated SEO title and meta description are injected into the HTML `<head>` tags of `templates/blog.html`, enabling search engine crawlers and social media preview bots (OpenGraph) to properly index the article.

---

## 👥 Acknowledgments
Developed for the **45-day Industrial Training Project** at **Codec Technologies**.
