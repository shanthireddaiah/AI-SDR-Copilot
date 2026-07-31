from django.db import models
from django.contrib.auth.models import User

class UploadedDocument(models.Model):
    """
    Stores PDF documents uploaded by users for RAG knowledge base retrieval.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255, help_text="Document Title or Description")
    file = models.FileField(upload_to='pdf_documents/', help_text="Uploaded PDF File")
    file_name = models.CharField(max_length=255, help_text="Original PDF File Name")
    chunk_count = models.IntegerField(default=0, help_text="Number of text chunks created")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.file_name})"
