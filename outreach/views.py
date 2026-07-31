from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import OutreachMessage
from .forms import OutreachForm
from .services import generate_outreach_content, export_as_pdf, export_as_txt
from research.models import Company
import json

@login_required
def generate_outreach_view(request):
    """
    Renders form to generate new sales outreach campaign.
    Generates cold email, follow-up, LinkedIn message, call script, or meeting request.
    """
    if request.method == 'POST':
        form = OutreachForm(request.POST, user=request.user)
        if form.is_valid():
            company = form.cleaned_data.get('company')
            manual_name = form.cleaned_data.get('company_name') or "Target Prospect"
            message_type = form.cleaned_data.get('message_type')
            target_role = form.cleaned_data.get('target_role') or "VP of Sales"

            result = generate_outreach_content(
                message_type=message_type,
                company=company,
                target_role=target_role,
                company_name=manual_name
            )

            outreach = OutreachMessage.objects.create(
                user=request.user,
                company=company,
                message_type=message_type,
                target_role=target_role,
                subject=result.get('subject', ''),
                content=result.get('content', '')
            )

            messages.success(request, f"New {outreach.get_message_type_display()} successfully generated!")
            return redirect('outreach:detail', pk=outreach.pk)
    else:
        form = OutreachForm(user=request.user)

    return render(request, 'outreach/generate.html', {'form': form})


@login_required
def outreach_list_view(request):
    """
    Displays paginated history of AI generated outreach messages with search filtering.
    """
    query = request.GET.get('q', '').strip()
    msg_type = request.GET.get('type', '').strip()

    messages_qs = OutreachMessage.objects.filter(user=request.user).select_related('company')

    if query:
        messages_qs = messages_qs.filter(
            Q(subject__icontains=query) |
            Q(content__icontains=query) |
            Q(company__name__icontains=query)
        )
    if msg_type:
        messages_qs = messages_qs.filter(message_type=msg_type)

    paginator = Paginator(messages_qs, 10) # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'selected_type': msg_type,
        'type_choices': OutreachMessage.MESSAGE_TYPE_CHOICES
    }
    return render(request, 'outreach/history.html', context)


@login_required
def outreach_detail_view(request, pk):
    """
    Displays single outreach message detail with options to copy, export PDF, or export TXT.
    """
    outreach = get_object_or_404(OutreachMessage.objects.select_related('company'), pk=pk, user=request.user)
    return render(request, 'outreach/detail.html', {'outreach': outreach})


@login_required
def export_outreach_pdf(request, pk):
    """
    Exports outreach message as PDF download.
    """
    outreach = get_object_or_404(OutreachMessage, pk=pk, user=request.user)
    pdf_bytes = export_as_pdf(outreach.subject or outreach.get_message_type_display(), outreach.content)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    filename = f"Outreach_{outreach.id}_{outreach.message_type}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def export_outreach_txt(request, pk):
    """
    Exports outreach message as plain text file download.
    """
    outreach = get_object_or_404(OutreachMessage, pk=pk, user=request.user)
    txt_bytes = export_as_txt(outreach.subject or outreach.get_message_type_display(), outreach.content)

    response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
    filename = f"Outreach_{outreach.id}_{outreach.message_type}.txt"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def api_generate_outreach(request):
    """
    REST API endpoint for outreach generation (POST JSON).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        company_id = data.get('company_id')
        manual_name = data.get('company_name', 'Target Prospect')
        message_type = data.get('message_type', 'cold_email')
        target_role = data.get('target_role', 'VP of Sales')

        company = None
        if company_id:
            company = Company.objects.filter(id=company_id, user=request.user).first()

        result = generate_outreach_content(
            message_type=message_type,
            company=company,
            target_role=target_role,
            company_name=manual_name
        )

        outreach = OutreachMessage.objects.create(
            user=request.user,
            company=company,
            message_type=message_type,
            target_role=target_role,
            subject=result.get('subject', ''),
            content=result.get('content', '')
        )

        return JsonResponse({
            'status': 'success',
            'id': outreach.id,
            'message_type': outreach.message_type,
            'subject': outreach.subject,
            'content': outreach.content,
            'created_at': outreach.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
