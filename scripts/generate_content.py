import os
import sys
import time
import random
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
TOPICS = [
    "Top 5 AI Tools for Coding in 2026",
    "How to Automate your Daily Emails with Python and AI",
    "The Future of Web Development with AI Agents",
    "Building Custom GPTs for Small Business Analytics",
    "Smart Home Automation Hacks using AI",
    "Productivity Boost: AI Tools that replaced my Assistant",
    "Understanding LLMs: A Guide for Non-Technical Founders",
    "AI in 2026: What to expect next?",
    "Best VS Code Extensions for AI-Assisted Programming",
    "How to use Gemini 2.0 for Data Analysis",
    "Generative AI for Marketing: A Practical Guide",
    "Cybersecurity in the Age of AI: What You Need to Know",
    "No-Code AI App Builders: Review 2026",
    "Machine Learning for Beginners: Where to Start"
]

IMAGES = [
    '/images/blog/article-1.jpg', '/images/blog/article-2.jpg', '/images/blog/article-3.jpg',
    '/images/blog/article-4.jpg', '/images/blog/article-5.jpg', '/images/blog/article-6.jpg',
    '/images/blog/article-7.jpg', '/images/blog/article-8.jpg', '/images/blog/article-9.jpg',
    '/images/blog/article-10.jpg', '/images/blog/article-11.jpg', '/images/blog/article-12.jpg',
    '/images/blog/article-13.jpg', '/images/blog/article-14.jpg', '/images/blog/article-15.jpg'
]

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("Warning: GEMINI_API_KEY environment variable not set.")
        return None
    return key

def generate_article():
    api_key = get_api_key()
    if not api_key:
        return None, "Error: API Key missing"

    # Configure the SDK
    genai.configure(api_key=api_key)

    topic = random.choice(TOPICS)
    print(f"Generating article on: {topic}...")

    prompt = f"""
    You are the Lead Editor of SmartAIHacks, a tech-savvy, forward-thinking blog about AI, Coding, and Productivity.
    Write a SEO-optimized blog post about: "{topic}".

    RULES:
    1. Tone: Professional, enthusiastic, practical, and futuristic (Year 2026 context).
    2. Structure: 
       - Catchy Title (H1) - Do not include "Title:" prefix.
       - Engaging Introduction.
       - Actionable Steps/Tips (use H2 and H3).
       - Conclusion.
    3. Content: Focus on "Hacks", specific tools, and "How-to" value. Avoid fluff.
    4. Format: Return ONLY the content in Markdown format. 
       - Do NOT include frontmatter (metadata) at the top, I will add it programmatically.
       - Do NOT wrap the entire output in markdown code blocks (```markdown). Just raw markdown.
    """

    for attempt in range(3):
        try:
            # Try Primary Model (Stable Flash 1.5)
            try:
                print(f"Attempt {attempt+1}: Trying gemini-1.5-flash...")
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                return response.text, topic
            
            except Exception as e_primary:
                print(f"Primary model failed: {e_primary}")
                
                # Try Fallback (Gemini Pro)
                try:
                    print(f"Attempt {attempt+1}: Switching to fallback model (gemini-1.5-pro)...")
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(prompt)
                    return response.text, topic
                except Exception as e_fallback:
                    print(f"Fallback model failed: {e_fallback}")
                    # Re-raise to trigger the outer except block retry logic if needed
                    raise e_fallback

        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                print(f"Quota exceeded, retrying in 60s... ({attempt+1}/3)")
                time.sleep(60)
            else:
                print(f"Error generating content: {e}")
                # Don't retry immediately on non-quota errors, or just let the loop continue
    
    return None, "Error: Failed after 3 attempts"

def save_file(content, title):
    if not content:
        return

    # Create slug
    slug = title.lower().strip().replace(" ", "-")
    # Remove special chars
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{slug}.md"
    
    destination = os.path.join("src", "content", "blog")
    os.makedirs(destination, exist_ok=True)
    full_path = os.path.join(destination, filename)

    image_path = random.choice(IMAGES)
    
    # Remove any potential markdown code blocks if the LLM added them
    content = content.replace("```markdown", "").replace("```", "").strip()

    final_content = f"""---
title: '{title.replace("'", "''")}'
description: "Discover the latest insights on {title} and how it transforms your workflow in 2026."
pubDate: {date_str}
author: 'SmartAI Team'
image: '{image_path}'
---

{content}
"""
    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        print(f"Success! Saved to {full_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    text, title = generate_article()
    if text and "Error" not in title:
        save_file(text, title)
    else:
        sys.exit(1)
