from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import UploadedDocument
from .services import extract_pdf_text, chunk_text
import os

class RagTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rag_user', password='password123')
        self.client = Client()
        self.client.login(username='rag_user', password='password123')

    def test_chunk_text_function(self):
        sample_text = "Paragraph 1 sentence.\n\nParagraph 2 sentence.\n\nParagraph 3 sentence."
        chunks = chunk_text(sample_text, chunk_size=30, chunk_overlap=5)
        self.assertGreater(len(chunks), 0)

    def test_uploaded_document_model(self):
        pdf = SimpleUploadedFile("sample.pdf", b"%PDF-1.4 sample content", content_type="application/pdf")
        doc = UploadedDocument.objects.create(
            user=self.user,
            title="Sample Sales Doc",
            file=pdf,
            file_name="sample.pdf"
        )
        self.assertEqual(UploadedDocument.objects.count(), 1)
        self.assertEqual(doc.title, "Sample Sales Doc")

    def test_knowledge_base_view(self):
        response = self.client.get('/rag/')
        self.assertEqual(response.status_code, 200)
