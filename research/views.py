from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Company
from .forms import CompanyResearchForm
from .services import generate_company_research, generate_outreach_messages
from outreach.services import export_as_pdf, export_as_txt
import json

@login_required
def research_form_view(request):
    """
    Renders research form and triggers AI Company Research generation engine.
    """
    if request.method == 'POST':
        form = CompanyResearchForm(request.POST)
        if form.is_valid():
            company_instance = form.save(commit=False)
            company_instance.user = request.user

            # Step 1: Generate AI Research Insights
            research_data = generate_company_research(
                name=company_instance.name,
                website=company_instance.website or "",
                industry=company_instance.industry or "",
                description=company_instance.user_description or ""
            )

            company_instance.overview = research_data.get('overview')
            company_instance.products = research_data.get('products')
            company_instance.pain_points = research_data.get('pain_points')
            company_instance.sales_insights = research_data.get('sales_insights')

            # Step 2: Generate Initial Outreach Templates
            outreach_data = generate_outreach_messages(
                company_name=company_instance.name,
                industry=company_instance.industry or "",
                overview=company_instance.overview or "",
                products=company_instance.products or "",
                pain_points=company_instance.pain_points or ""
            )

            company_instance.email_outreach = outreach_data.get('email_outreach')
            company_instance.linkedin_outreach = outreach_data.get('linkedin_outreach')
            company_instance.cold_call_script = outreach_data.get('cold_call_script')

            company_instance.save()

            messages.success(request, f"AI Research successfully generated for {company_instance.name}!")
            return redirect('research:detail', pk=company_instance.pk)
        else:
            messages.error(request, "Please check the form inputs and try again.")
    else:
        form = CompanyResearchForm()

    return render(request, 'research/company.html', {'form': form})


@login_required
def research_detail_view(request, pk):
    """
    Displays full detailed research output for a company.
    """
    company = get_object_or_404(Company, pk=pk, user=request.user)
    return render(request, 'research/company_detail.html', {'company': company})


@login_required
def company_history_view(request):
    """
    Displays paginated list of target companies with search & filtering.
    """
    query = request.GET.get('q', '').strip()
    industry_filter = request.GET.get('industry', '').strip()

    companies = Company.objects.filter(user=request.user)

    if query:
        companies = companies.filter(
            Q(name__icontains=query) |
            Q(industry__icontains=query) |
            Q(overview__icontains=query)
        )

    if industry_filter:
        companies = companies.filter(industry__icontains=industry_filter)

    paginator = Paginator(companies, 10) # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'industry_filter': industry_filter
    }
    return render(request, 'research/history.html', context)


@login_required
def export_company_pdf(request, pk):
    """
    Exports company research report as a PDF download.
    """
    company = get_object_or_404(Company, pk=pk, user=request.user)
    title = f"AI Research Brief: {company.name}"
    content = f"""COMPANY OVERVIEW:
{company.overview or 'N/A'}

PRODUCTS & SERVICES:
{company.products or 'N/A'}

CUSTOMER PAIN POINTS:
{company.pain_points or 'N/A'}

SALES OUTREACH INSIGHTS:
{company.sales_insights or 'N/A'}
"""

    pdf_bytes = export_as_pdf(title, content)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Research_{company.name}.pdf"'
    return response


@login_required
def export_company_txt(request, pk):
    """
    Exports company research report as plain text download.
    """
    company = get_object_or_404(Company, pk=pk, user=request.user)
    title = f"AI Research Brief: {company.name}"
    content = f"""COMPANY OVERVIEW:
{company.overview or 'N/A'}

PRODUCTS & SERVICES:
{company.products or 'N/A'}

CUSTOMER PAIN POINTS:
{company.pain_points or 'N/A'}

SALES OUTREACH INSIGHTS:
{company.sales_insights or 'N/A'}
"""

    txt_bytes = export_as_txt(title, content)
    response = HttpResponse(txt_bytes, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Research_{company.name}.txt"'
    return response


# --- REST API ENDPOINTS ---

@login_required
def api_company_list(request):
    """
    REST API to list or submit research for target companies (JSON).
    """
    if request.method == 'GET':
        companies = Company.objects.filter(user=request.user)[:50]
        data = [{
            'id': c.id,
            'name': c.name,
            'website': c.website,
            'industry': c.industry,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for c in companies]
        return JsonResponse({'status': 'success', 'count': len(data), 'companies': data})

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            name = body.get('name')
            if not name:
                return JsonResponse({'error': 'Company name is required'}, status=400)

            website = body.get('website', '')
            industry = body.get('industry', '')
            description = body.get('user_description', '')

            research_data = generate_company_research(name, website, industry, description)
            outreach_data = generate_outreach_messages(name, industry, research_data.get('overview'), research_data.get('products'), research_data.get('pain_points'))

            company = Company.objects.create(
                user=request.user,
                name=name,
                website=website,
                industry=industry,
                user_description=description,
                overview=research_data.get('overview'),
                products=research_data.get('products'),
                pain_points=research_data.get('pain_points'),
                sales_insights=research_data.get('sales_insights'),
                email_outreach=outreach_data.get('email_outreach'),
                linkedin_outreach=outreach_data.get('linkedin_outreach'),
                cold_call_script=outreach_data.get('cold_call_script')
            )

            return JsonResponse({
                'status': 'success',
                'id': company.id,
                'name': company.name,
                'overview': company.overview,
                'products': company.products,
                'pain_points': company.pain_points,
                'sales_insights': company.sales_insights
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def api_company_detail(request, pk):
    """
    REST API to retrieve full details of a specific company.
    """
    company = get_object_or_404(Company, pk=pk, user=request.user)
    return JsonResponse({
        'id': company.id,
        'name': company.name,
        'website': company.website,
        'industry': company.industry,
        'overview': company.overview,
        'products': company.products,
        'pain_points': company.pain_points,
        'sales_insights': company.sales_insights,
        'email_outreach': company.email_outreach,
        'linkedin_outreach': company.linkedin_outreach,
        'cold_call_script': company.cold_call_script,
        'created_at': company.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })
