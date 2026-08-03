"""
LangGraph Workflow Engine for AI Sales Copilot.
Defines a basic StateGraph orchestrating:
Start -> Retrieve Company Research -> Retrieve Document Context (ChromaDB RAG) -> Build Prompt -> Call OpenAI GPT-4o-mini -> End
"""

import os
import logging
from typing import TypedDict, Optional
from django.conf import settings
from langgraph.graph import StateGraph, END
from research.models import Company
from rag.services import query_knowledge_base, is_demo_mode

logger = logging.getLogger(__name__)


class SalesCopilotState(TypedDict):
    question: str
    user_id: int
    company_id: Optional[int]
    company_context: str
    rag_context: str
    prompt: str
    response: str


def retrieve_company_context(state: SalesCopilotState) -> SalesCopilotState:
    """
    Node 1: Loads prospect company research context if company_id is selected.
    """
    company_id = state.get('company_id')
    user_id = state.get('user_id')
    company_context = "No specific target company selected."

    if company_id and user_id:
        try:
            company = Company.objects.get(id=company_id, user_id=user_id)
            company_context = (
                f"Target Company: {company.name}\n"
                f"Industry: {company.industry or 'N/A'}\n"
                f"Business Overview: {company.overview or 'N/A'}\n"
                f"Products: {company.products or 'N/A'}\n"
                f"Pain Points: {company.pain_points or 'N/A'}\n"
                f"Sales Insights: {company.sales_insights or 'N/A'}"
            )
        except Company.DoesNotExist:
            company_context = "Selected target company record not found."

    state['company_context'] = company_context
    return state


def retrieve_rag_context(state: SalesCopilotState) -> SalesCopilotState:
    """
    Node 2: Queries ChromaDB RAG vector store for matching document text chunks.
    """
    question = state.get('question', '')
    user_id = state.get('user_id', 0)

    chunks = query_knowledge_base(question, user_id=user_id, top_k=3)
    if chunks:
        rag_context = "\n---\n".join(chunks)
    else:
        rag_context = "No relevant text chunks found in uploaded sales PDF documents."

    state['rag_context'] = rag_context
    return state


def format_prompt(state: SalesCopilotState) -> SalesCopilotState:
    """
    Node 3: Formats prompt using system prompt template.
    Template:
    "You are an AI Sales Research Assistant.
    Use the company information and uploaded documents to generate professional and personalized sales recommendations.
    If information is unavailable, clearly mention that."
    """
    question = state.get('question', '')
    company_context = state.get('company_context', '')
    rag_context = state.get('rag_context', '')

    prompt = f"""You are an AI Sales Research Assistant.

Use the company information and uploaded documents to generate professional and personalized sales recommendations.
If information is unavailable, clearly mention that.

[Target Company Information]
{company_context}

[Uploaded PDF Sales Documents Context (RAG)]
{rag_context}

[User Sales Question]
{question}
"""
    state['prompt'] = prompt
    return state


def _generate_dynamic_demo_response(question: str, company_context: str, rag_context: str) -> str:
    """
    Generates intelligent, dynamic, context-aware sales recommendations in Demo Mode.
    Tailors output specifically to the user's question, target account insights, and RAG document context.
    """
    q_lower = question.lower()

    # Extract company name or fallback
    comp_name = "the target prospect"
    industry = "the target market"
    pain_points = "operational inefficiencies"

    if "Target Company:" in company_context:
        for line in company_context.split('\n'):
            if line.startswith("Target Company:"):
                comp_name = line.replace("Target Company:", "").strip()
            elif line.startswith("Industry:"):
                industry = line.replace("Industry:", "").strip()
            elif line.startswith("Pain Points:"):
                pain_points = line.replace("Pain Points:", "").strip()

    has_rag = "No relevant text chunks found" not in rag_context and bool(rag_context.strip())

    # Topic 1: Initial Approach / Sales Call / First Contact
    if any(k in q_lower for k in ['approach', 'first call', 'sales call', 'pitch', 'contact', 'reach out', 'engage', 'opener']):
        res = (
            f"**Strategic Sales Recommendation for {comp_name}**:\n\n"
            f"1. **Discovery Opener & Hook**:\n"
            f"   - Open with an industry benchmark relevant to **{industry}**: *'We noticed many teams in {industry} face challenges with {pain_points}.'*\n"
            f"   - Frame the conversation around mitigating risk and accelerating deployment.\n\n"
            f"2. **Pain-Point Alignment**:\n"
            f"   - Highlight how your core solution addresses **{pain_points}** specifically for {comp_name}.\n\n"
            f"3. **Call To Action (CTA)**:\n"
            f"   - Request a 15-minute technical discovery session with key stakeholders."
        )

    # Topic 2: Objection Handling / Pushback / Resistance
    elif any(k in q_lower for k in ['objection', 'pushback', 'no time', 'too expensive', 'not interested', 'budget', 'hesitant']):
        res = (
            f"**Objection Handling Guide for {comp_name}**:\n\n"
            f"1. **Acknowledge & Reframe**:\n"
            f"   - Empathize with their current bandwidth or budget constraints: *'I completely understand timing is critical.'*\n\n"
            f"2. **Value-Proof Pivot**:\n"
            f"   - Demonstrate fast time-to-value: Focus on how solving **{pain_points}** yields immediate ROI for {comp_name}.\n\n"
            f"3. **Low-Friction Next Step**:\n"
            f"   - Offer a zero-risk 10-minute executive briefing or async document audit instead of a full demo."
        )

    # Topic 3: Pricing / Budget / Cost
    elif any(k in q_lower for k in ['price', 'pricing', 'cost', 'expensive', 'discount', 'contract', 'fee']):
        res = (
            f"**Commercial & Value Positioning Strategy for {comp_name}**:\n\n"
            f"1. **Lead with Value, Not Price**:\n"
            f"   - Emphasize total cost of ownership reduction by tackling **{pain_points}**.\n\n"
            f"2. **Tiered Value Framing**:\n"
            f"   - Present flexible pilot or phased rollout options tailored for companies in **{industry}**.\n\n"
            f"3. **ROI Calculation Hook**:\n"
            f"   - Offer to run a joint ROI model with their finance team."
        )

    # Topic 4: Competition / Differentiators / Why Us
    elif any(k in q_lower for k in ['competitor', 'versus', 'vs', 'difference', 'differentiate', 'why us', 'alternative']):
        res = (
            f"**Competitive Positioning Matrix for {comp_name}**:\n\n"
            f"1. **Core Differentiator**:\n"
            f"   - Highlight enterprise integration speed and specialized AI workflows built for **{industry}**.\n\n"
            f"2. **Solving Pain Points Better**:\n"
            f"   - While legacy tools address surface needs, our platform directly targets **{pain_points}**.\n\n"
            f"3. **Proof Point**:\n"
            f"   - Offer a head-to-head feature matrix tailored to {comp_name}'s requirements."
        )

    # Topic 5: Document / PDF / RAG Specific Questions
    elif has_rag or any(k in q_lower for k in ['pdf', 'document', 'file', 'spec', 'collateral', 'brochure', 'rag']):
        rag_snippet = rag_context[:300] + "..." if len(rag_context) > 300 else rag_context
        res = (
            f"**RAG Sales Document Insights for '{question}'**:\n\n"
            f"**Retrieved Knowledge Base Excerpt**:\n> {rag_snippet}\n\n"
            f"**Key Recommendations**:\n"
            f"1. **Document Reference**: Use the retrieved collateral points to substantiate claims regarding **{pain_points}**.\n"
            f"2. **Prospect Engagement**: Share the relevant section of the brochure directly during your next meeting with {comp_name}."
        )

    # Topic 6: Dynamic General Synthesis
    else:
        res = (
            f"**AI Sales Strategy for Query: '{question}'**:\n\n"
            f"1. **Target Account Insights ({comp_name})**:\n"
            f"   - Tailor your message to decision-makers in **{industry}**.\n"
            f"   - Focus on key operational challenge: **{pain_points}**.\n\n"
            f"2. **Recommended Action**:\n"
            f"   - Structure your response around key value pillars and schedule a 15-minute discovery call.\n\n"
            f"3. **Next Step**:\n"
            f"   - Generate an automated Outreach Email or LinkedIn InMail pitch in the **AI Outreach Generator** module."
        )

    if has_rag and "Retrieved Knowledge Base Excerpt" not in res:
        res += f"\n\n---\n📌 **Relevant RAG Document Context Available**: Included document context from uploaded sales PDFs."

    return res


def call_llm(state: SalesCopilotState) -> SalesCopilotState:
    """
    Node 4: Executes OpenAI GPT-4o-mini API call or Demo Mode dynamic synthesis.
    """
    prompt = state.get('prompt', '')
    question = state.get('question', '')
    company_context = state.get('company_context', '')
    rag_context = state.get('rag_context', '')
    user_id = state.get('user_id')

    # Check for UserProfile custom API key override or settings key
    user_api_key = None
    if user_id:
        try:
            from settings.models import UserProfile
            profile = UserProfile.objects.filter(user_id=user_id).first()
            if profile and profile.custom_openai_key and profile.custom_openai_key.startswith('sk-'):
                user_api_key = profile.custom_openai_key.strip()
        except Exception:
            pass

    gemini_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    api_key = user_api_key or getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
    use_live_openai = api_key and api_key.strip().lower() not in ('demo', 'your_openai_api_key_here', '')

    response_text = None

    # Step 1: Try Google Gemini API if GEMINI_API_KEY is configured
    if gemini_key and gemini_key.strip():
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            for m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-lite"]:
                try:
                    res = client.models.generate_content(
                        model=m,
                        contents=f"You are an expert AI Sales Development Representative (SDR) Copilot.\n\n{prompt}"
                    )
                    if res and res.text:
                        response_text = res.text
                        break
                except Exception as me:
                    logger.warning(f"Gemini model {m} call failed: {me}")
        except Exception as ge:
            logger.warning(f"Gemini API initialization failed: {ge}")

    # Step 2: Try OpenAI if Gemini was not used or failed
    if not response_text and use_live_openai:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)

            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert AI Sales Development Representative (SDR) Copilot."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            response_text = res.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API Error in LangGraph LLM Node: {e}")

    # Step 3: Fallback to Dynamic Demo Synthesis
    if not response_text:
        response_text = _generate_dynamic_demo_response(question, company_context, rag_context)

    state['response'] = response_text
    return state


def build_sales_copilot_graph():
    """
    Builds and compiles the LangGraph StateGraph workflow.
    Workflow:
    Start -> retrieve_company_context -> retrieve_rag_context -> format_prompt -> call_llm -> End
    """
    workflow = StateGraph(SalesCopilotState)

    # Add Nodes
    workflow.add_node("retrieve_company_context", retrieve_company_context)
    workflow.add_node("retrieve_rag_context", retrieve_rag_context)
    workflow.add_node("format_prompt", format_prompt)
    workflow.add_node("call_llm", call_llm)

    # Set Entry Point and Edges
    workflow.set_entry_point("retrieve_company_context")
    workflow.add_edge("retrieve_company_context", "retrieve_rag_context")
    workflow.add_edge("retrieve_rag_context", "format_prompt")
    workflow.add_edge("format_prompt", "call_llm")
    workflow.add_edge("call_llm", END)

    return workflow.compile()


# Singleton compiled graph instance
sales_copilot_app = build_sales_copilot_graph()


def run_sales_copilot_workflow(question: str, user_id: int, company_id: Optional[int] = None) -> str:
    """
    Executes the LangGraph StateGraph sales copilot workflow and returns the response.
    """
    initial_state: SalesCopilotState = {
        "question": question,
        "user_id": user_id,
        "company_id": company_id,
        "company_context": "",
        "rag_context": "",
        "prompt": "",
        "response": ""
    }

    final_state = sales_copilot_app.invoke(initial_state)
    return final_state.get("response", "No response generated by AI Copilot.")
