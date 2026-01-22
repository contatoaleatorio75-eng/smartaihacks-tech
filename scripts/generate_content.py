import os
import sys
import time
import random
from datetime import datetime
from google import genai

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

def list_debug_models(client):
    print("\n--- DEBUG: Listing Available Models ---")
    try:
        # Attempt to list models to see what the API key has access to
        for model in client.models.list():
            print(f"Found: {model.name}")
        print("---------------------------------------")
    except Exception as e:
        print(f"Failed to list models: {e}")

def generate_article():
    api_key = get_api_key()
    if not api_key:
        return None, "Error: API Key missing"

    client = genai.Client(api_key=api_key)

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

    # List of models to try in order of preference/stability
    # We prioritize 1.5 Flash versions that are usually free/stable
    model_candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-2.0-flash" # Last resort due to quota issues seen
    ]

    for model_name in model_candidates:
        print(f"Trying model: {model_name}...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            print(f"Success with {model_name}!")
            return response.text, topic
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE" in msg:
                print(f"Quota exceeded for {model_name}. Skipping to next...")
            elif "404" in msg:
                print(f"Model {model_name} not found (404). Skipping...")
            else:
                print(f"Error with {model_name}: {e}")
            
            # small delay before next attempt
            time.sleep(1)

    # If we get here, all models failed. Let's list what IS available to help debug.
    print("\nAll attempts failed. Running debug info...")
    list_debug_models(client)
    
    return None, "Error: All models failed"

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
