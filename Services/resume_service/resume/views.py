from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Resume
from .serializers import ResumeSerializer
import fitz  # PyMuPDF
import re
import logging
import requests
from bson import ObjectId

# Configure logging
logger = logging.getLogger(__name__)

class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        job_id = self.request.data.get('job_id')
        name = self.request.data.get('name')
        email = self.request.data.get('email')

        if not self.validate_job_id(job_id):
            logger.error('Invalid job ID')
            raise ValidationError({'job_id': 'Invalid job ID'})

        # Extract details from the uploaded resume
        resume_file = self.request.data.get('resume_file')
        text = self.extract_text_from_pdf(resume_file)
        sections = self.extract_sections(text)

        instance = serializer.save(
            job_id=job_id,
            name=name,
            email=email,
            education=sections.get('education', 'Education not found'),
            experience=sections.get('experience', 'Experience not found'),
            skills=sections.get('technical skills', 'Skills not found'),
            projects=sections.get('projects', 'Projects not found'),
            text=text
        )

    def validate_job_id(self, job_id):
        try:
            job_id_obj = ObjectId(job_id)  # Validate job_id as ObjectId
        except Exception as e:
            logger.error(f"Invalid job ID format: {e}")
            return False

        job_service_url = f'http://127.0.0.1:8000/api/jobs/{job_id}/'
        try:
            response = requests.get(job_service_url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return False
        except Exception as err:
            logger.error(f"Other error occurred: {err}")
            return False

        job_data = response.json()
        logger.info(f"Job data: {job_data}")
        return str(job_data.get('_id')) == str(job_id_obj)

    def extract_text_from_pdf(self, pdf_file):
        document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ''
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text

    def extract_sections(self, text):
        sections = {
            'skills': '',
            'relevant_coursework': '',
            'experience': '',
            'education': '',
            'projects': ''
        }

        section_patterns = {
            'skills': re.compile(r'\btechnical skills\b', re.IGNORECASE),
            'relevant_coursework': re.compile(r'\brelevant coursework\b', re.IGNORECASE),
            'experience': re.compile(r'\bexperience\b', re.IGNORECASE),
            'education': re.compile(r'\beducation\b', re.IGNORECASE),
            'projects': re.compile(r'\bprojects\b', re.IGNORECASE)
        }

        current_section = None
        for line in text.split('\n'):
            line_lower = line.lower().strip()
            for section, pattern in section_patterns.items():
                if pattern.search(line_lower):
                    current_section = section
                    break
            if current_section:
                sections[current_section] += line + '\n'

        for section in sections:
            sections[section] = sections[section].replace(section, '', 1).strip()

        return sections

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
