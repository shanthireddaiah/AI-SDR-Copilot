from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ChatHistory
from research.models import Company
from .graph import run_sales_copilot_workflow
from outreach.services import export_as_pdf, export_as_txt
import json

@login_required
def copilot_chat_view(request):
    """
    Renders AI Sales Copilot chat interface and processes Q&A queries using LangGraph workflow.
    """
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        company_id_raw = request.POST.get('company_id', None)
        
        company_id = int(company_id_raw) if company_id_raw and str(company_id_raw).isdigit() else None

        if not question:
            messages.error(request, "Question cannot be empty.")
            return redirect('chat:index')

        try:
            answer = run_sales_copilot_workflow(
                question=question,
                user_id=request.user.id,
                company_id=company_id
            )

            company_obj = Company.objects.filter(id=company_id, user=request.user).first() if company_id else None
            ChatHistory.objects.create(
                user=request.user,
                company=company_obj,
                question=question,
                answer=answer
            )

            messages.success(request, "AI Sales Copilot recommendation generated!")

        except Exception as e:
            messages.error(request, f"Error running Sales Copilot workflow: {str(e)}")

        return redirect('chat:index')

    history_qs = ChatHistory.objects.filter(user=request.user).select_related('company').order_by('timestamp')
    companies = Company.objects.filter(user=request.user)

    paginator = Paginator(history_qs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'chat/copilot.html', {
        'page_obj': page_obj,
        'history': history_qs,
        'companies': companies
    })


@login_required
def chat_history_list_view(request):
    """
    Dedicated view displaying searchable paginated AI Chat history.
    """
    query = request.GET.get('q', '').strip()
    history_qs = ChatHistory.objects.filter(user=request.user).select_related('company')

    if query:
        history_qs = history_qs.filter(Q(question__icontains=query) | Q(answer__icontains=query))

    paginator = Paginator(history_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'chat/history.html', {'page_obj': page_obj, 'query': query})


@login_required
def export_chat_pdf(request, pk):
    """
    Exports single chat session to PDF file download.
    """
    chat = get_object_or_404(ChatHistory, pk=pk, user=request.user)
    title = f"AI Sales Copilot Chat ({chat.timestamp.strftime('%Y-%m-%d')})"
    content = f"USER QUESTION:\n{chat.question}\n\nAI COPILOT RESPONSE:\n{chat.answer}"

    pdf_bytes = export_as_pdf(title, content)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Chat_Session_{chat.id}.pdf"'
    return response


@login_required
def export_chat_txt(request, pk):
    """
    Exports single chat session to plain text download.
    """
    chat = get_object_or_404(ChatHistory, pk=pk, user=request.user)
    title = f"AI Sales Copilot Chat ({chat.timestamp.strftime('%Y-%m-%d')})"
    content = f"USER QUESTION:\n{chat.question}\n\nAI COPILOT RESPONSE:\n{chat.answer}"

    txt_bytes = export_as_txt(title, content)
    response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Chat_Session_{chat.id}.txt"'
    return response


# --- REST APIs ---

@login_required
@require_http_methods(["POST"])
def api_chat_post(request):
    """
    REST API: POST /chat/api/
    Executes LangGraph workflow and stores session in MySQL database.
    """
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    question = data.get('question', '').strip()
    company_id_raw = data.get('company_id')
    company_id = int(company_id_raw) if company_id_raw and str(company_id_raw).isdigit() else None

    if not question:
        return JsonResponse({'error': 'Question field is required.'}, status=400)

    try:
        answer = run_sales_copilot_workflow(
            question=question,
            user_id=request.user.id,
            company_id=company_id
        )

        company_obj = Company.objects.filter(id=company_id, user=request.user).first() if company_id else None
        chat = ChatHistory.objects.create(
            user=request.user,
            company=company_obj,
            question=question,
            answer=answer
        )

        return JsonResponse({
            'status': 'success',
            'chat_id': chat.id,
            'question': chat.question,
            'answer': chat.answer,
            'company': chat.company.name if chat.company else None,
            'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def api_chat_history(request):
    """
    REST API: GET /chat/api/history/
    """
    history = ChatHistory.objects.filter(user=request.user).select_related('company')[:50]
    data = [
        {
            'id': item.id,
            'question': item.question,
            'answer': item.answer,
            'company': item.company.name if item.company else None,
            'timestamp': item.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for item in history
    ]
    return JsonResponse({'status': 'success', 'count': len(data), 'history': data})
