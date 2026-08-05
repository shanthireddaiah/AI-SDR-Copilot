"""
Outreach Generation Engine & Export Service.
Supports OpenAI GPT-4o-mini integration & zero-dependency Demo Mode.
Generates 5 distinct sales formats: Cold Email, Follow-up Email, LinkedIn Message, Sales Call Script, Meeting Request.
Provides PDF and TXT export utilities.
"""

import os
import logging
from io import BytesIO
from django.conf import settings
from research.services import is_demo_mode

logger = logging.getLogger(__name__)

def generate_outreach_content(message_type, company=None, target_role="VP of Sales", company_name="Target Prospect"):
    """
    Generates AI outreach copy for the specified message format.
    Uses OpenAI GPT-4o-mini when API key is valid; otherwise generates rich Demo Mode copy.
    """
    comp_name = company.name if company else company_name
    comp_industry = company.industry if (company and company.industry) else "Technology Solutions"
    comp_pain = company.pain_points if (company and company.pain_points) else "scaling operations efficiently"
    comp_overview = company.overview if (company and company.overview) else "Leading enterprise solutions provider"

    gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    if gemini_key and gemini_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            prompt_template = f"""You are an elite Sales Development Representative (SDR).
Generate a highly personalized, high-converting {message_type} for a prospect.

Target Company: {comp_name}
Industry: {comp_industry}
Target Role / Persona: {target_role}
Company Overview: {comp_overview}
Pain Points to Target: {comp_pain}

Instructions:
1. Keep the tone professional, persuasive, and concise.
2. Provide a compelling subject line (if applicable).
3. Focus on driving a 15-minute discovery call.
"""
            for m in ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=prompt_template
                    )
                    if res and res.text:
                        content = res.text
                        subject = f"Unlocking Growth for {comp_name}"
                        if "Subject:" in content:
                            lines = content.split('\n')
                            for line in lines:
                                if line.startswith("Subject:"):
                                    subject = line.replace("Subject:", "").strip()
                                    break
                        return {"subject": subject, "content": content}
                except Exception as me:
                    logger.warning(f"Gemini outreach model {m} call failed: {me}")
        except Exception as ge:
            logger.warning(f"Gemini Outreach Generation Error: {ge}")

    if is_demo_mode():
        return _generate_demo_outreach(message_type, comp_name, comp_industry, target_role, comp_pain)

    try:
        from openai import OpenAI
        api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key)

        prompt_template = f"""You are an elite Sales Development Representative (SDR).
Generate a highly personalized, high-converting {message_type} for a prospect.

Target Company: {comp_name}
Industry: {comp_industry}
Target Role / Persona: {target_role}
Company Overview: {comp_overview}
Pain Points to Target: {comp_pain}

Instructions:
1. Keep the tone professional, persuasive, and concise.
2. Provide a compelling subject line (if applicable).
3. Focus on driving a 15-minute discovery call.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a top-performing B2B Sales Development Representative."},
                {"role": "user", "content": prompt_template}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content
        subject = f"Unlocking Growth for {comp_name}"
        if "Subject:" in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith("Subject:"):
                    subject = line.replace("Subject:", "").strip()
                    break

        return {"subject": subject, "content": content}

    except Exception as e:
        logger.error(f"OpenAI Outreach Generation Error: {e}")
        return _generate_demo_outreach(message_type, comp_name, comp_industry, target_role, comp_pain)


def _generate_demo_outreach(message_type, comp_name, comp_industry, target_role, comp_pain):
    """
    Generates rich, realistic outreach copy for Demo Mode.
    """
    if message_type == 'cold_email':
        subject = f"Quick question regarding {comp_name}'s growth initiatives"
        content = f"""Hi {target_role},

I hope this message finds you well.

I’ve been following {comp_name}'s work in the {comp_industry} space and was thoroughly impressed by your recent expansion.

Many teams in {comp_industry} struggle with {comp_pain}. We helped a similar enterprise reduce operational friction by 35% within 90 days.

Would you be open to a quick 10-minute chat this Thursday at 2 PM to explore how we can deliver similar outcomes for {comp_name}?

Best regards,
AI SDR Assistant"""

    elif message_type == 'follow_up':
        subject = f"Re: Quick question regarding {comp_name}"
        content = f"""Hi {target_role},

Following up on my previous email regarding {comp_name}'s goals for this quarter.

I understand your schedule is tight. I wanted to share a brief 1-page case study demonstrating how our framework addresses {comp_pain}.

Do you have 5 minutes next Tuesday morning for a brief call?

Best,
AI SDR Assistant"""

    elif message_type == 'linkedin':
        subject = f"LinkedIn Connection: {comp_name}"
        content = f"""Hi {target_role}, noticed your leadership in {comp_industry} at {comp_name}. We're helping leaders tackle {comp_pain} with automated workflows. Would love to connect and share quick insights!"""

    elif message_type == 'call_script':
        subject = f"Sales Call Pitch for {comp_name}"
        content = f"""[Cold Call Script - Target: {target_role} at {comp_name}]

1. OPENEING (10 sec):
"Hi {target_role}, this is [Name]. I know I called out of the blue, do you have 30 seconds for me to tell you why I reached out?"

2. VALUE PROP (20 sec):
"We specialize in helping {comp_industry} leaders like {comp_name} eliminate {comp_pain}."

3. DISCOVERY QUESTION:
"How are you currently managing these workflows today?"

4. CALL TO ACTION:
"Let's book 15 minutes next Tuesday to review a tailored walkthrough. Does morning work better for you?"
"""

    elif message_type == 'meeting_req':
        subject = f"Meeting Request: AI Strategy Session for {comp_name}"
        content = f"""Dear {target_role},

I would like to invite you to an exclusive 15-minute executive briefing tailored specifically for {comp_name}.

Agenda:
- Benchmark analysis against {comp_industry} industry standards.
- Strategies for mitigating {comp_pain}.
- Live demonstration of automated workflow capabilities.

Please let me know if Tuesday or Wednesday works best for your schedule.

Sincerely,
AI SDR Assistant"""

    else:
        subject = f"Outreach for {comp_name}"
        content = f"Custom outreach pitch generated for {comp_name} targeting {target_role}."

    return {"subject": subject, "content": content}


def export_as_txt(title, content):
    """
    Generates downloadable plain text buffer.
    """
    output = f"=== {title.upper()} ===\n\n{content}\n"
    return output.encode('utf-8')


def export_as_pdf(title, content):
    """
    Generates downloadable PDF buffer using ReportLab or fallback plaintext formatter.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceAfter=12
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=8
        )

        elements = []
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # Format line breaks into paragraphs
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                clean_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                elements.append(Paragraph(clean_line, body_style))
            else:
                elements.append(Spacer(1, 6))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        logger.warning(f"ReportLab PDF export fallback triggered: {e}")
        # Plain text fallback returned if reportlab fails
        return export_as_txt(title, content)
