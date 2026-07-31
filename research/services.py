"""
AI Services module for Company Research & Sales Outreach Generation.
Supports OpenAI API (gpt-4o-mini) and an automatic Demo Mode fallback 
when OPENAI_API_KEY is not configured or set to 'demo'.
"""

import os
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def is_demo_mode():
    """
    Checks if the application is running in Demo Mode.
    Returns False if GEMINI_API_KEY or OPENAI_API_KEY is configured.
    """
    gemini_key = os.getenv('GEMINI_API_KEY', '') or getattr(settings, 'GEMINI_API_KEY', '')
    if gemini_key and gemini_key.strip():
        return False

    api_key = getattr(settings, 'OPENAI_API_KEY', 'demo') or os.getenv('OPENAI_API_KEY', 'demo')
    return not api_key or api_key.strip().lower() in ('demo', 'your_openai_api_key_here', '')


def fetch_live_website_text(url):
    """
    Fetches and extracts plain text from a live website URL in real-time.
    """
    if not url:
        return ""
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url

    try:
        import urllib.request
        from html.parser import HTMLParser

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text_list = []
                self.ignore = False
                self.ignored_tags = {'script', 'style', 'head', 'title', 'meta', '[document]'}

            def handle_starttag(self, tag, attrs):
                if tag.lower() in self.ignored_tags:
                    self.ignore = True

            def handle_endtag(self, tag):
                if tag.lower() in self.ignored_tags:
                    self.ignore = False

            def handle_data(self, data):
                if not self.ignore and data.strip():
                    self.text_list.append(data.strip())

        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'}
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            html_content = resp.read().decode('utf-8', errors='ignore')
            parser = TextExtractor()
            parser.feed(html_content)
            extracted = " ".join(parser.text_list[:120])
            return extracted[:1200]
    except Exception as e:
        logger.warning(f"[LIVE WEB SCRAPE] Could not fetch live content from '{url}': {e}")
        return ""


def generate_company_research(name, website="", industry="", description=""):
    """
    Generates structured AI research for a prospect company.
    Fetches real-time live online data from website URL if available.
    """
    # Fetch real-time live web data from prospect website URL if provided
    live_web_text = fetch_live_website_text(website) if website else ""

    # Demo Mode Fallback
    if is_demo_mode():
        ind = industry if industry else "Technology & Enterprise SaaS"
        desc = description if description else (live_web_text[:250] if live_web_text else f"{name} provides high-impact solutions for modern organizations.")

        web_snippet_info = f" (Scraped Live Web Data: '{live_web_text[:180]}...')" if live_web_text else ""

        return {
            "overview": f"{name} is an enterprise leader in the {ind} sector. {desc}{web_snippet_info} They focus on driving digital innovation, operational efficiency, and scalable business outcomes.",
            "products": f"1. {name} Core Enterprise Suite: Fully integrated management platform.\n2. Intelligent Automation: Streamlined workflows and real-time analytics.\n3. Custom API & Cloud Services: Scalable infrastructure.",
            "pain_points": f"• Operational overhead caused by fragmented legacy tools.\n• Scalability bottlenecks when handling expanding enterprise customer data.\n• Urgent need for automated reporting, security compliance, and team collaboration.",
            "sales_insights": f"• Decision-makers at {name} prioritize fast ROI and seamless deployment.\n• Pitching integrated automation directly addresses identified operational friction.\n• Emphasize robust security compliance and fast time-to-value."
        }

    gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            You are an expert AI Sales Development Representative (SDR) Research Assistant.
            Analyze the following prospect company information and generate structured sales insights in valid JSON format.

            Company Name: {name}
            Website: {website}
            Industry: {industry}
            User Provided Description: {description}
            Live Web Scraped Content from Website: {live_web_text}

            Respond ONLY with a JSON object containing these exact keys:
            - "overview": A concise business overview (2-3 paragraphs).
            - "products": Key products and services offered.
            - "pain_points": 3-4 likely customer or operational pain points.
            - "sales_insights": 3-4 actionable AI-generated sales outreach recommendations.
            """
            for m in ["gemma-4-31b-it", "gemma-4-26b-a4b-it", "gemini-2.0-flash-lite"]:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=prompt
                    )
                    if res and res.text:
                        raw = res.text.strip()
                        if raw.startswith("```json"):
                            raw = raw[7:]
                        if raw.endswith("```"):
                            raw = raw[:-3]
                        data = json.loads(raw.strip())
                        return {
                            "overview": data.get("overview", "Overview unavailable."),
                            "products": data.get("products", "Products information unavailable."),
                            "pain_points": data.get("pain_points", "Pain points unavailable."),
                            "sales_insights": data.get("sales_insights", "Sales insights unavailable.")
                        }
                except Exception as me:
                    logger.warning(f"Gemini research model {m} call failed: {me}")
        except Exception as ge:
            logger.warning(f"Gemini API Company Research Error: {ge}")

    # Live OpenAI API Integration
    try:
        from openai import OpenAI
        api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        prompt = f"""
        You are an expert AI Sales Development Representative (SDR) Research Assistant.
        Analyze the following prospect company information and generate structured sales insights in valid JSON format.

        Company Name: {name}
        Website: {website}
        Industry: {industry}
        User Provided Description: {description}
        Live Web Scraped Content from Website: {live_web_text}

        Respond ONLY with a JSON object containing these exact keys:
        - "overview": A concise business overview (2-3 paragraphs).
        - "products": Key products and services offered.
        - "pain_points": 3-4 likely customer or operational pain points.
        - "sales_insights": 3-4 actionable AI-generated sales outreach recommendations.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI Sales Assistant. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return {
            "overview": data.get("overview", "Overview unavailable."),
            "products": data.get("products", "Products information unavailable."),
            "pain_points": data.get("pain_points", "Pain points unavailable."),
            "sales_insights": data.get("sales_insights", "Sales insights unavailable.")
        }

    except Exception as e:
        logger.error(f"OpenAI API Error during company research: {e}")
        # Fallback to dynamic demo synthesis with live web data
        ind = industry if industry else "Technology & Enterprise SaaS"
        desc = description if description else (live_web_text[:250] if live_web_text else f"{name} provides high-impact solutions for modern organizations.")
        web_snippet_info = f" (Scraped Live Web Data: '{live_web_text[:180]}...')" if live_web_text else ""

        return {
            "overview": f"{name} is an enterprise leader in the {ind} sector. {desc}{web_snippet_info}",
            "products": f"1. {name} Core Enterprise Suite: Fully integrated management platform.\n2. Intelligent Automation: Streamlined workflows and real-time analytics.",
            "pain_points": f"• Operational overhead caused by fragmented legacy tools.\n• Scalability bottlenecks when handling expanding enterprise customer data.",
            "sales_insights": f"• Decision-makers at {name} prioritize fast ROI and seamless deployment.\n• Pitching integrated automation directly addresses identified operational friction."
        }


def generate_outreach_messages(company_name, industry="", overview="", products="", pain_points=""):
    """
    Generates personalized multi-channel sales outreach messages:
    - Personalized Cold Email
    - LinkedIn Direct Message
    - Cold Outreach Call Pitch
    """
    # Demo Mode Fallback
    if is_demo_mode():
        ind = industry if industry else "your sector"
        return {
            "email_outreach": f"Subject: Streamlining operational efficiency at {company_name}\n\nHi [Prospect Name],\n\nI noticed {company_name}'s recent growth in the {ind} space. Many teams we work with face challenges managing fragmented workflows and scaling operations efficiently.\n\nOur platform helps companies like yours streamline workflow automation and drive rapid ROI without replacing your core stack.\n\nWould you be open to a brief 10-minute chat next Tuesday to explore if this could benefit {company_name}?\n\nBest regards,\n[Your Name]\nSales Development Representative",
            "linkedin_outreach": f"Hi [Prospect Name], impressed by {company_name}'s work in {ind}! We're helping enterprise teams automate sales research and outreach workflows. Would love to connect and share a 2-minute overview if you're open to it.",
            "cold_call_script": f"1. Opener: 'Hi [Prospect Name], this is [Your Name] from AI SDR Copilot. I know I caught you out of the blue, do you have 30 seconds?'\n2. Value Hook: 'We help sales leaders at companies like {company_name} eliminate manual research and generate hyper-personalized outreach in seconds.'\n3. Qualifying Question: 'How is your team currently gathering company intelligence before initial calls?'\n4. Call to Action: 'I'd love to schedule a brief 10-minute demo this Thursday. Does morning or afternoon work better for you?'"
        }

    # Live OpenAI API Integration
    try:
        from openai import OpenAI
        api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        prompt = f"""
        You are an elite Sales Copywriter and SDR. Based on the target company research below, generate personalized outreach copy.

        Company Name: {company_name}
        Industry: {industry}
        Overview: {overview}
        Products: {products}
        Pain Points: {pain_points}

        Generate ONLY a JSON object containing:
        - "email_outreach": A compelling, highly personalized cold email draft with Subject line.
        - "linkedin_outreach": A short, high-converting LinkedIn direct message (under 300 characters).
        - "cold_call_script": A structured cold call phone script (Opener, Hook, Question, Call to Action).
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional sales copywriter. Output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content
        data = json.loads(content)
        return {
            "email_outreach": data.get("email_outreach", "Email copy unavailable."),
            "linkedin_outreach": data.get("linkedin_outreach", "LinkedIn copy unavailable."),
            "cold_call_script": data.get("cold_call_script", "Cold call script unavailable.")
        }

    except Exception as e:
        logger.error(f"OpenAI API Error during outreach generation: {e}")
        return {
            "email_outreach": f"Subject: Partnering with {company_name}\n\nHi [Prospect Name],\n\nHope this email finds you well. I wanted to reach out regarding {company_name}'s growth...",
            "linkedin_outreach": f"Hi [Prospect Name], would love to connect and share how we help companies in {industry or 'your industry'} scale outreach.",
            "cold_call_script": f"Hi [Prospect Name], this is [Your Name]. We help teams at {company_name} optimize sales research..."
        }
