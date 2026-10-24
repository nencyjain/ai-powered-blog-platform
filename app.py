"""
=============================================================================
Project: AI-Powered Blog Platform
Description: A beginner-friendly web application built for a 45-day
             industrial training project at Codec Technologies.
Tech Stack: Python Flask, HTML5, CSS3, JavaScript, OpenAI API, JSON Storage.
=============================================================================
"""

import os
import json
import uuid
import re
import html
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
from markupsafe import Markup

# Try loading environment variables from .env if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing openai if installed
try:
    import openai
    HAS_OPENAI_LIB = True
except ImportError:
    HAS_OPENAI_LIB = False

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "codec-tech-training-default-secret-key-2026")

# Path to the JSON data storage file
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "blogs.json")


# =============================================================================
# Helper Functions: JSON Storage (Database Operations)
# =============================================================================

def ensure_data_file():
    """Ensure that the data directory and blogs.json file exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def load_blogs():
    """
    Read and return all blog posts from data/blogs.json.
    Returns an empty list if file is empty or corrupted.
    """
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_blogs(blogs):
    """
    Save the list of blog posts into data/blogs.json with 2-space indentation.
    """
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=2, ensure_ascii=False)


def find_blog_by_id(blog_id):
    """Search and return a single blog post dictionary by its unique ID."""
    blogs = load_blogs()
    for blog in blogs:
        if blog.get("id") == blog_id:
            return blog
    return None


def generate_slug_id(title):
    """
    Generate a clean URL-friendly unique identifier from the blog title.
    Example: 'My First Post' -> 'my-first-post-a1b2c3'
    """
    clean = re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-')
    if not clean:
        clean = "post"
    random_suffix = uuid.uuid4().hex[:6]
    return f"{clean[:40]}-{random_suffix}"


# =============================================================================
# Helper Function: Markdown to HTML Converter (Safe & Zero-Dependency)
# =============================================================================

def render_markdown_to_html(text):
    """
    Convert markdown formatting into clean, secure HTML.
    Escapes all raw HTML first to prevent XSS (Cross-Site Scripting) attacks.
    """
    if not text:
        return Markup("")

    # 1. Sanitize user input by escaping existing HTML
    safe_text = html.escape(text)

    # 2. Extract and preserve code blocks (```python ... ```)
    def code_block_replacer(match):
        lang = match.group(1).strip()
        code = match.group(2).strip()
        lang_class = f' class="language-{lang}"' if lang else ""
        return f'<pre class="code-box"><code{lang_class}>{code}</code></pre>'

    safe_text = re.sub(r'```([a-zA-Z0-9_-]*)\r?\n(.*?)```', code_block_replacer, safe_text, flags=re.DOTALL)

    # 3. Process line by line for block elements (headings, quotes, lists)
    lines = safe_text.splitlines()
    output_lines = []
    in_ul = False
    in_ol = False

    for line in lines:
        stripped = line.strip()

        # Headings (H1, H2, H3, H4)
        if stripped.startswith("#### "):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(f"<h4>{stripped[5:]}</h4>")
        elif stripped.startswith("### "):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("## "):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("# "):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(f"<h1>{stripped[2:]}</h1>")
        # Blockquote
        elif stripped.startswith("&gt; ") or stripped.startswith("> "):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            quote_text = stripped[5:] if stripped.startswith("&gt; ") else stripped[2:]
            output_lines.append(f'<blockquote class="blog-quote">{quote_text}</blockquote>')
        # Bullet list item
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if in_ol: output_lines.append("</ol>"); in_ol = False
            if not in_ul:
                output_lines.append('<ul class="blog-list">')
                in_ul = True
            output_lines.append(f"<li>{stripped[2:]}</li>")
        # Numbered list item
        elif re.match(r'^\d+\.\s', stripped):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if not in_ol:
                output_lines.append('<ol class="blog-ordered-list">')
                in_ol = True
            item_content = re.sub(r'^\d+\.\s', '', stripped)
            output_lines.append(f"<li>{item_content}</li>")
        # Horizontal Rule
        elif stripped in ("---", "***", "___"):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append('<hr class="divider">')
        # Empty line
        elif not stripped:
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append("")
        # Preformatted code blocks or regular paragraph
        elif stripped.startswith('<pre class="code-box">'):
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(stripped)
        else:
            if in_ul: output_lines.append("</ul>"); in_ul = False
            if in_ol: output_lines.append("</ol>"); in_ol = False
            output_lines.append(f"<p>{stripped}</p>")

    if in_ul:
        output_lines.append("</ul>")
    if in_ol:
        output_lines.append("</ol>")

    result = "\n".join(output_lines)

    # 4. Inline formatting: bold, italic, code, links
    result = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'\*(.+?)\*', r'<em>\1</em>', result)
    result = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', result)
    result = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer" class="blog-link">\1</a>', result)

    return Markup(result)


# =============================================================================
# Helper Functions: AI Generation and Demo Mode Generator
# =============================================================================

def is_api_key_configured():
    """
    Check if a valid, non-placeholder OpenAI API key is set.
    Returns True only if OPENAI_API_KEY is present and not a dummy placeholder.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(api_key and api_key != "your_openai_api_key_here")


def get_openai_client():
    """
    Returns an initialized OpenAI client if OPENAI_API_KEY is configured
    and the library is available. Otherwise returns None.
    """
    if not is_api_key_configured():
        return None
    if not HAS_OPENAI_LIB:
        return None
    try:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        return openai.OpenAI(api_key=api_key)
    except Exception:
        return None


def generate_demo_blog(topic, tone, length):
    """
    Generates high-quality, structured sample blog content for Demo Mode.
    Guarantees the application functions 100% without needing an API key.
    """
    topic_clean = topic.strip() or "Modern Technology Trends"
    tone_clean = tone.capitalize() if tone else "Professional"
    length_clean = length.lower() if length else "medium"

    # Tone customization intro styles
    tone_intros = {
        "Professional": f"In today's fast-evolving landscape, understanding **{topic_clean}** has become a critical strategic advantage for professionals and organizations alike.",
        "Friendly": f"Hey there! If you have been curious about **{topic_clean}** recently, you are in the right spot! Let's explore together how this is changing our everyday lives.",
        "Educational": f"The purpose of this guide is to break down the core principles of **{topic_clean}** into accessible, step-by-step concepts for learners of all levels.",
        "Casual": f"Let's be honest: everyone is talking about **{topic_clean}** these days. But what's the actual story behind the hype? Let's dive in!"
    }
    intro_text = tone_intros.get(tone_clean, tone_intros["Professional"])

    # Base structured content
    title = f"Mastering {topic_clean}: A Comprehensive Guide"
    
    sections = [
        f"# {title}\n",
        f"{intro_text}\n",
        f"## 1. Why {topic_clean} Matters Now\n",
        f"Whether you are a student, an engineer, or an industry practitioner, **{topic_clean}** represents an important shift in how we solve problems and build modern solutions.\n",
        "- **Efficiency:** Streamlines manual workflows and enhances productivity.",
        "- **Scalability:** Enables scalable systems that adapt to dynamic user demands.",
        "- **Innovation:** Unlocks fresh creative possibilities across diverse domains.\n",
        f"## 2. Key Pillars of {topic_clean}\n",
        f"To truly grasp the fundamentals, keep these three foundational pillars in mind:\n",
        f"1. **Core Fundamentals:** Master the basic theoretical concepts before diving into advanced tooling.\n"
        f"2. **Hands-on Experimentation:** Build small prototypes to reinforce your learning.\n"
        f"3. **Continuous Iteration:** Stay updated with community best practices and documentation.\n",
        f"> \"Continuous learning is the minimum requirement for success in any technical discipline.\"\n"
    ]

    # Expand for medium / long length
    if length_clean in ("medium", "long"):
        sections.extend([
            f"## 3. Practical Best Practices\n",
            f"When implementing solutions related to **{topic_clean}**, always follow structured engineering guidelines:\n",
            f"- Keep your implementation modular and easy to maintain.\n",
            f"- Validate all external inputs to ensure security and data integrity.\n",
            f"- Write descriptive documentation and comments for your team members.\n",
            f"```python\n# Example workflow for {re.sub(r'[^a-zA-Z0-9_]', '_', topic_clean).lower()}\ndef execute_pipeline(data):\n    print('Processing {topic_clean} workflow...')\n    return {{'status': 'success', 'records': len(data)}}\n```\n"
        ])

    if length_clean == "long":
        sections.extend([
            f"## 4. Addressing Common Challenges\n",
            f"Adopting new technologies frequently introduces hurdles. Here is how you can mitigate the most common pitfalls:\n",
            f"- **Information Overload:** Focus on official documentation and verified case studies.\n",
            f"- **Debugging Complexity:** Use structured logging and monitoring to trace errors.\n",
            f"- **Future-Proofing:** Design flexible architectures that tolerate evolving requirements.\n"
        ])

    sections.extend([
        f"## Conclusion\n",
        f"In summary, **{topic_clean}** is an exciting domain with tremendous potential. By combining solid theoretical principles with consistent hands-on practice, you can build meaningful projects and stay ahead of the curve."
    ])

    content = "\n".join(sections)
    return {
        "title": title,
        "content": content,
        "is_demo": True,
        "notice": "DEMO MODE ACTIVE: This content was generated using the built-in demo engine because no OpenAI API key was detected in .env."
    }


def generate_demo_seo(topic, content):
    """Generate realistic SEO recommendations for Demo Mode."""
    clean_topic = topic.strip() or "Tech Guide"
    meta_title = f"{clean_topic} Guide (2026) | Complete Overview & Tips"[:60]
    meta_description = f"Discover actionable insights, best practices, and a complete breakdown of {clean_topic}. Learn how to get started effectively."[:160]
    
    words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', clean_topic)]
    keywords_list = list(dict.fromkeys(words + ["tutorial", "guide", "best practices", "technology"]))[:5]
    keywords = ", ".join(keywords_list)

    return {
        "meta_title": meta_title,
        "meta_description": meta_description,
        "keywords": keywords,
        "is_demo": True
    }


# =============================================================================
# Routes: Page Views (Frontend Templates)
# =============================================================================

@app.route("/")
def index():
    """
    Dashboard Page:
    Displays project overview, total/published/draft blog counters,
    and lists all saved blog posts.
    """
    blogs = load_blogs()
    # Sort posts so newest appear first
    blogs_sorted = sorted(blogs, key=lambda b: b.get("updated_at", b.get("created_at", "")), reverse=True)

    total_count = len(blogs_sorted)
    published_count = sum(1 for b in blogs_sorted if b.get("status") == "published")
    draft_count = sum(1 for b in blogs_sorted if b.get("status") == "draft")

    api_configured = bool(os.getenv("OPENAI_API_KEY", "").strip() and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here")

    return render_template(
        "index.html",
        blogs=blogs_sorted,
        total_count=total_count,
        published_count=published_count,
        draft_count=draft_count,
        api_configured=api_configured
    )


@app.route("/editor")
@app.route("/editor/<blog_id>")
def editor(blog_id=None):
    """
    Blog Editor Page:
    Can be loaded empty (for a new post) or pre-populated with an existing blog's data.
    """
    blog = None
    if blog_id:
        blog = find_blog_by_id(blog_id)
        if not blog:
            return redirect(url_for("index"))

    api_configured = bool(os.getenv("OPENAI_API_KEY", "").strip() and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here")

    return render_template(
        "editor.html",
        blog=blog,
        api_configured=api_configured
    )


@app.route("/blog/<blog_id>")
def view_blog(blog_id):
    """
    Public Blog Reading Page:
    Displays the formatted blog post with markdown converted to HTML and SEO metadata.
    """
    blog = find_blog_by_id(blog_id)
    if not blog:
        return render_template("blog.html", blog=None), 404

    # Convert stored markdown into secure HTML
    rendered_html = render_markdown_to_html(blog.get("content", ""))

    # Calculate estimated reading time (~200 words per minute)
    word_count = len(re.findall(r'\w+', blog.get("content", "")))
    read_time_minutes = max(1, round(word_count / 200))

    return render_template(
        "blog.html",
        blog=blog,
        content_html=rendered_html,
        word_count=word_count,
        read_time_minutes=read_time_minutes
    )


# =============================================================================
# API Endpoints: Generation & CRUD Operations
# =============================================================================

@app.route("/api/status", methods=["GET"])
def api_status():
    """Returns current environment status and AI configuration."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    is_key_set = bool(api_key and api_key != "your_openai_api_key_here")
    force_demo = os.getenv("FORCE_DEMO_MODE", "false").lower() == "true"

    return jsonify({
        "status": "success",
        "openai_installed": HAS_OPENAI_LIB,
        "api_key_configured": is_key_set,
        "demo_mode_active": force_demo or (not is_key_set),
        "total_blogs": len(load_blogs())
    })


@app.route("/api/generate", methods=["POST"])
def api_generate():
    """
    Generate Blog Post Content using OpenAI API or the built-in Demo Mode.
    Accepts: { topic: str, tone: str, length: str, mode: str, force_demo: bool }
    """
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()
    tone = data.get("tone", "Professional").strip()
    length = data.get("length", "Medium").strip()
    mode = data.get("mode", "auto").strip().lower()
    user_requested_demo = data.get("force_demo", False)

    if not topic:
        return jsonify({"status": "error", "message": "Please enter a blog topic before generating."}), 400

    force_demo = os.getenv("FORCE_DEMO_MODE", "false").lower() == "true" or user_requested_demo
    has_key = is_api_key_configured()

    # 1. Demo Mode: Generate content locally with zero external network requests
    if mode == "demo" or force_demo or (mode != "openai" and not has_key):
        demo_result = generate_demo_blog(topic, tone, length)
        return jsonify({
            "status": "success",
            "is_demo": True,
            "title": demo_result["title"],
            "content": demo_result["content"],
            "message": "Demo Mode: Sample blog generated locally without external API."
        })

    # 2. Live OpenAI Mode: Explicitly requested live generation
    if not has_key:
        return jsonify({
            "status": "error",
            "message": "OpenAI API key is missing. Please set OPENAI_API_KEY in your .env file to enable live AI generation, or switch to Demo Mode."
        }), 400

    if not HAS_OPENAI_LIB:
        return jsonify({
            "status": "error",
            "message": "The 'openai' Python library is not installed. Run 'pip install openai' or use Demo Mode."
        }), 400

    client = get_openai_client()
    if not client:
        return jsonify({
            "status": "error",
            "message": "Could not initialize OpenAI client. Please check your OPENAI_API_KEY in .env."
        }), 400

    # Call OpenAI API
    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        word_counts = {"Short": "300 to 450", "Medium": "600 to 800", "Long": "1000 to 1300"}
        target_words = word_counts.get(length, "600 to 800")

        prompt = (
            f"You are a professional blog writer. Generate a well-structured blog post in clean Markdown format.\n"
            f"Topic: {topic}\n"
            f"Tone: {tone}\n"
            f"Length: Approximately {target_words} words ({length} length)\n\n"
            f"Requirements:\n"
            f"1. Start with a compelling H1 title: # [Title Here]\n"
            f"2. Write an engaging introductory paragraph.\n"
            f"3. Use H2 (##) and H3 (###) subheadings for main concepts.\n"
            f"4. Include bullet points or numbered lists where helpful.\n"
            f"5. Include a relevant blockquote or key takeaway callout.\n"
            f"6. End with an H2 ## Conclusion section summarizing key points.\n"
            f"7. Return ONLY the markdown content, no extra conversational preamble."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional content creator and technical blogger."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        full_content = response.choices[0].message.content.strip()

        # Extract title from first line if it starts with #
        lines = full_content.splitlines()
        title = topic.title()
        if lines and lines[0].startswith("# "):
            title = lines[0].replace("# ", "").strip()

        return jsonify({
            "status": "success",
            "is_demo": False,
            "title": title,
            "content": full_content,
            "message": f"Successfully generated using OpenAI ({model})."
        })

    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            user_msg = "Invalid OpenAI API Key. Please verify your key in .env or switch to Demo Mode."
        elif "quota" in error_msg.lower() or "rate" in error_msg.lower():
            user_msg = "OpenAI quota exceeded or rate limit reached. Please switch to Demo Mode."
        else:
            user_msg = f"AI Generation failed: {error_msg}. Try switching to Demo Mode."

        return jsonify({
            "status": "error",
            "message": user_msg,
            "can_fallback_demo": True
        }), 400


@app.route("/api/generate-seo", methods=["POST"])
def api_generate_seo():
    """
    Generate SEO Title, Meta Description, and Suggested Keywords.
    Accepts: { topic: str, content: str, mode: str, force_demo: bool }
    """
    data = request.get_json() or {}
    topic = data.get("topic", "").strip()
    content = data.get("content", "").strip()
    mode = data.get("mode", "auto").strip().lower()
    user_requested_demo = data.get("force_demo", False)

    if not topic and not content:
        return jsonify({"status": "error", "message": "Please enter a topic or write some content to generate SEO suggestions."}), 400

    force_demo = os.getenv("FORCE_DEMO_MODE", "false").lower() == "true" or user_requested_demo
    has_key = is_api_key_configured()

    # 1. Demo Mode: Generate SEO metadata locally with zero external network requests
    if mode == "demo" or force_demo or (mode != "openai" and not has_key):
        demo_seo = generate_demo_seo(topic, content)
        return jsonify({
            "status": "success",
            "is_demo": True,
            "seo": demo_seo,
            "message": "Demo Mode: SEO metadata generated locally without external API."
        })

    # 2. Live OpenAI Mode: Explicitly requested live generation
    if not has_key:
        return jsonify({
            "status": "error",
            "message": "OpenAI API key is missing. Please set OPENAI_API_KEY in your .env file to enable live AI SEO generation, or use Demo Mode."
        }), 400

    if not HAS_OPENAI_LIB:
        return jsonify({
            "status": "error",
            "message": "The 'openai' library is not installed. Run 'pip install openai' or use Demo Mode."
        }), 400

    client = get_openai_client()
    if not client:
        return jsonify({
            "status": "error",
            "message": "Could not initialize OpenAI client. Check your OPENAI_API_KEY in .env."
        }), 400

    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        prompt = (
            f"You are an expert SEO specialist. Based on the following blog topic and content summary, "
            f"generate optimized SEO metadata.\n\n"
            f"Topic: {topic}\n"
            f"Content sample: {content[:800]}\n\n"
            f"Return a strict JSON object with these EXACT keys:\n"
            f"- meta_title: An SEO title under 60 characters with high search intent.\n"
            f"- meta_description: A compelling meta description between 130 and 155 characters.\n"
            f"- keywords: A comma-separated string of 4-6 target keywords.\n"
            f"Return ONLY raw JSON, with no markdown code fences or other text."
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional SEO analyst. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )

        raw_output = response.choices[0].message.content.strip()
        raw_output = re.sub(r'^```(json)?\s*', '', raw_output)
        raw_output = re.sub(r'\s*```$', '', raw_output)
        seo_data = json.loads(raw_output)

        return jsonify({
            "status": "success",
            "is_demo": False,
            "seo": {
                "meta_title": seo_data.get("meta_title", f"{topic} | Complete Guide")[:60],
                "meta_description": seo_data.get("meta_description", f"Learn everything about {topic}.")[:160],
                "keywords": seo_data.get("keywords", f"{topic}, guide, 2026")
            },
            "message": "SEO metadata generated successfully via OpenAI."
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"OpenAI SEO generation failed: {str(e)}. You can switch to Demo Mode."
        }), 400


@app.route("/api/blogs", methods=["POST"])
def api_save_blog():
    """Save a new blog post (as either 'draft' or 'published')."""
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    status = data.get("status", "draft").strip().lower()

    if status not in ("draft", "published"):
        status = "draft"

    if not title:
        return jsonify({"status": "error", "message": "Blog title cannot be empty."}), 400
    if not content:
        return jsonify({"status": "error", "message": "Blog content cannot be empty."}), 400

    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    new_id = generate_slug_id(title)

    new_blog = {
        "id": new_id,
        "title": title,
        "topic": data.get("topic", "").strip(),
        "tone": data.get("tone", "Professional"),
        "length": data.get("length", "Medium"),
        "content": content,
        "status": status,
        "created_at": now_str,
        "updated_at": now_str,
        "seo": {
            "meta_title": data.get("seo", {}).get("meta_title", title)[:60],
            "meta_description": data.get("seo", {}).get("meta_description", "")[:160],
            "keywords": data.get("seo", {}).get("keywords", "")
        }
    }

    blogs = load_blogs()
    blogs.append(new_blog)
    save_blogs(blogs)

    return jsonify({
        "status": "success",
        "message": f"Blog post successfully saved as {status}!",
        "blog_id": new_id
    }), 201


@app.route("/api/blogs/<blog_id>", methods=["PUT"])
def api_update_blog(blog_id):
    """Update an existing blog post."""
    data = request.get_json() or {}
    blogs = load_blogs()

    for idx, blog in enumerate(blogs):
        if blog.get("id") == blog_id:
            # Update fields
            if "title" in data and data["title"].strip():
                blog["title"] = data["title"].strip()
            if "content" in data and data["content"].strip():
                blog["content"] = data["content"].strip()
            if "status" in data and data["status"] in ("draft", "published"):
                blog["status"] = data["status"]
            if "topic" in data:
                blog["topic"] = data["topic"].strip()
            if "tone" in data:
                blog["tone"] = data["tone"]
            if "length" in data:
                blog["length"] = data["length"]

            if "seo" in data and isinstance(data["seo"], dict):
                blog["seo"] = {
                    "meta_title": data["seo"].get("meta_title", blog["title"])[:60],
                    "meta_description": data["seo"].get("meta_description", "")[:160],
                    "keywords": data["seo"].get("keywords", "")
                }

            blog["updated_at"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
            blogs[idx] = blog
            save_blogs(blogs)

            return jsonify({
                "status": "success",
                "message": "Blog updated successfully!",
                "blog_id": blog_id
            })

    return jsonify({"status": "error", "message": "Blog not found."}), 404


@app.route("/api/blogs/<blog_id>", methods=["DELETE"])
def api_delete_blog(blog_id):
    """Delete a blog post by ID from the JSON database."""
    blogs = load_blogs()
    initial_length = len(blogs)
    blogs_remaining = [b for b in blogs if b.get("id") != blog_id]

    if len(blogs_remaining) == initial_length:
        return jsonify({"status": "error", "message": "Blog post not found."}), 404

    save_blogs(blogs_remaining)
    return jsonify({
        "status": "success",
        "message": "Blog post deleted successfully."
    })


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == "__main__":
    # Ensure data directory exists on startup
    ensure_data_file()
    print("=======================================================")
    print("  AI-Powered Blog Platform (Codec Technologies Project)")
    print("  Server running on http://127.0.0.1:5000")
    print("=======================================================")
    app.run(host="127.0.0.1", port=5000, debug=True)
