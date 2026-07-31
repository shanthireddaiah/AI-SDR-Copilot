from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from research.models import Company
from rag.models import UploadedDocument
from chat.models import ChatHistory
from outreach.models import OutreachMessage

@login_required
def index_view(request):
    """
    Renders the main SDR Research Copilot Dashboard.
    Calculates summary metrics & loads recent activities:
    - Total Companies Researched
    - Total PDF Documents Uploaded
    - Total Outreach Campaigns Generated
    - Total AI Chat Conversations
    - Global Search Query across all modules
    """
    query = request.GET.get('q', '').strip()

    total_companies = Company.objects.filter(user=request.user).count()
    uploaded_docs = UploadedDocument.objects.filter(user=request.user).count()
    total_outreach = OutreachMessage.objects.filter(user=request.user).count()
    total_chats = ChatHistory.objects.filter(user=request.user).count()

    recent_companies = Company.objects.filter(user=request.user)[:5]
    recent_outreach = OutreachMessage.objects.filter(user=request.user).select_related('company')[:5]
    recent_chats = ChatHistory.objects.filter(user=request.user).select_related('company')[:5]

    search_results = {}
    if query:
        search_results['companies'] = Company.objects.filter(
            user=request.user
        ).filter(Q(name__icontains=query) | Q(industry__icontains=query))[:10]

        search_results['documents'] = UploadedDocument.objects.filter(
            user=request.user
        ).filter(Q(title__icontains=query) | Q(file_name__icontains=query))[:10]

        search_results['outreach'] = OutreachMessage.objects.filter(
            user=request.user
        ).filter(Q(subject__icontains=query) | Q(content__icontains=query))[:10]

        search_results['chats'] = ChatHistory.objects.filter(
            user=request.user
        ).filter(Q(question__icontains=query) | Q(answer__icontains=query))[:10]

    # Dynamic notification events
    notifications = [
        {'title': 'System Ready', 'time': 'Just now', 'type': 'info', 'desc': 'AI SDR Copilot system initialized and ready.'},
        {'title': 'Demo Mode Active', 'time': 'Active', 'type': 'success', 'desc': 'Operating with built-in AI intelligence and ChromaDB vector store.'}
    ]

    context = {
        'total_companies': total_companies,
        'uploaded_docs': uploaded_docs,
        'total_outreach': total_outreach,
        'total_chats': total_chats,
        'recent_companies': recent_companies,
        'recent_outreach': recent_outreach,
        'recent_chats': recent_chats,
        'query': query,
        'search_results': search_results,
        'notifications': notifications
    }

    return render(request, 'dashboard/index.html', context)
