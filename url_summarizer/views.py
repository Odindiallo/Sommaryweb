from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
import json
from .crew import URLSummarizer
from documentation.models import Document
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid
import re

# Load environment variables
load_dotenv()

def extract_markdown_content(html_content):
    """Convert HTML content back to markdown-like format."""
    # Remove any HTML tags but preserve line breaks
    content = re.sub(r'<[^>]+>', '', html_content)
    
    # Convert multiple spaces to single space
    content = re.sub(r'\s+', ' ', content)
    
    # Add proper markdown headings
    lines = content.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        # Handle headings
        if 'Title:' in line:
            line = f"# {line.replace('Title:', '').strip()}"
        elif line.strip().endswith(':'):
            line = f"## {line.strip()}"
            
        # Handle list items
        if line.strip().startswith('- '):
            if not in_list:
                formatted_lines.append('')  # Add space before list
                in_list = True
        else:
            in_list = False
            
        formatted_lines.append(line)
    
    return '\n\n'.join(formatted_lines)

@login_required
def summarizer_view(request):
    return render(request, 'url_summarizer/summarizer.html')

@csrf_exempt
@require_http_methods(["POST"])
def summarize_url(request):
    try:
        data = json.loads(request.body)
        url = data.get('url')
        
        if not url:
            return JsonResponse({'error': 'URL is required'}, status=400)
            
        # Check if OpenAI API key is available
        if not os.getenv('OPENAI_API_KEY'):
            return JsonResponse({'error': 'OpenAI API key not configured'}, status=500)
        
        try:    
            summarizer = URLSummarizer()
            summary = summarizer.get_summary(url)
            return JsonResponse({'summary': summary})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_document(request):
    try:
        data = json.loads(request.body)
        summary = data.get('summary', '')
        title = data.get('title', 'URL Summary')
        
        if not summary:
            return JsonResponse({'error': 'Summary is required'}, status=400)
        
        # Generate a unique slug
        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1
        
        # Keep trying until we find a unique slug
        while Document.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1
            
        # Create document with the original markdown content
        document = Document.objects.create(
            title=title,
            content=summary,  # Use the original summary content
            author=request.user,
            slug=unique_slug,
            is_public=True
        )
        
        return JsonResponse({
            'message': 'Document created successfully',
            'document_id': document.id,
            'document_slug': document.slug
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Failed to create document: {str(e)}'}, status=500)
