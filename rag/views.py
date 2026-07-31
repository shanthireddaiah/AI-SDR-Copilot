import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import UploadedDocument
from .services import process_and_embed_pdf, delete_document_vectors, query_knowledge_base, is_demo_mode

@login_required
def knowledge_base_view(request):
    """
    Renders RAG Knowledge Base interface and handles PDF document uploads & deletions.
    """
    if request.method == 'POST':
        action = request.POST.get('action', 'upload')

        # Action 1: Delete PDF Document & Purge Vectors from ChromaDB
        if action == 'delete':
            doc_id = request.POST.get('doc_id')
            doc = get_object_or_404(UploadedDocument, id=doc_id, user=request.user)
            doc_title = doc.title
            
            try:
                delete_document_vectors(doc.id)
                if doc.file and os.path.exists(doc.file.path):
                    os.remove(doc.file.path)
                doc.delete()
                messages.success(request, f"Document '{doc_title}' and vector embeddings purged successfully!")
            except Exception as e:
                messages.error(request, f"Error deleting document: {str(e)}")

            return redirect('rag:index')

        # Action 2: Process New PDF Upload
        title = request.POST.get('title', '').strip()
        pdf_file = request.FILES.get('pdf_file')

        if not title:
            messages.error(request, "Document Title is required.")
            return redirect('rag:index')

        if not pdf_file:
            messages.error(request, "Please select a PDF file to upload.")
            return redirect('rag:index')

        if not pdf_file.name.lower().endswith('.pdf'):
            messages.error(request, "Invalid file format. Please upload a valid PDF document (.pdf).")
            return redirect('rag:index')

        try:
            doc = UploadedDocument.objects.create(
                user=request.user,
                title=title,
                file=pdf_file,
                file_name=pdf_file.name
            )

            chunk_count = process_and_embed_pdf(doc)

            if is_demo_mode():
                messages.info(request, f"PDF '{doc.file_name}' processed in Demo Mode! ({chunk_count} text chunks stored in ChromaDB).")
            else:
                messages.success(request, f"PDF '{doc.file_name}' indexed in ChromaDB! ({chunk_count} text chunks embedded).")

        except ValueError as ve:
            messages.error(request, f"PDF Processing Warning: {str(ve)}")
        except Exception as e:
            messages.error(request, f"An error occurred during PDF processing: {str(e)}")

        return redirect('rag:index')

    query = request.GET.get('q', '').strip()
    documents = UploadedDocument.objects.filter(user=request.user)

    if query:
        documents = documents.filter(Q(title__icontains=query) | Q(file_name__icontains=query))

    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'rag/knowledge_base.html', {'page_obj': page_obj, 'query': query})


@login_required
def rag_query_ajax(request):
    """
    AJAX endpoint to query ChromaDB RAG vector store directly for relevant context chunks.
    """
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if not query:
            return JsonResponse({'error': 'Query text required'}, status=400)

        chunks = query_knowledge_base(query, user_id=request.user.id, top_k=3)
        return JsonResponse({
            'status': 'success',
            'query': query,
            'match_count': len(chunks),
            'chunks': chunks
        })

    return JsonResponse({'error': 'POST method required'}, status=405)


# --- REST API ENDPOINTS ---

@login_required
def api_upload_pdf(request):
    """
    REST API endpoint to upload and embed PDF files.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    title = request.POST.get('title', 'API Uploaded PDF')
    pdf_file = request.FILES.get('pdf_file')

    if not pdf_file or not pdf_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Valid PDF file required'}, status=400)

    try:
        doc = UploadedDocument.objects.create(
            user=request.user,
            title=title,
            file=pdf_file,
            file_name=pdf_file.name
        )

        chunk_count = process_and_embed_pdf(doc)
        return JsonResponse({
            'status': 'success',
            'doc_id': doc.id,
            'title': doc.title,
            'file_name': doc.file_name,
            'chunk_count': chunk_count
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_rag_query(request):
    """
    REST API endpoint for semantic RAG retrieval.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
        query = data.get('query', '').strip()
        top_k = data.get('top_k', 3)

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        chunks = query_knowledge_base(query, user_id=request.user.id, top_k=top_k)
        return JsonResponse({
            'status': 'success',
            'query': query,
            'results': chunks
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
