import logging
import requests
import openai
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings
from .models import ShortlistingRequest, ShortlistedCandidate
from .serializers import ShortlistingRequestSerializer, ShortlistedCandidateSerializer

# Configure logging
logger = logging.getLogger(__name__)

class ShortlistingRequestViewSet(viewsets.ModelViewSet):
    queryset = ShortlistingRequest.objects.all()
    serializer_class = ShortlistingRequestSerializer
    parser_classes = [JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shortlisting_request = serializer.save()

        job_id = shortlisting_request.job_id
        num_candidates = shortlisting_request.num_candidates

        # Fetch job description from Job Service
        job_response = requests.get(f'http://localhost:8000/api/jobs/{job_id}/')
        logger.info(f"Job Service Response: {job_response.status_code}, {job_response.text}")

        if job_response.status_code != 200:
            return Response({"error": "Failed to fetch job description"}, status=job_response.status_code)

        try:
            job_description = job_response.json().get('description')
        except ValueError:
            return Response({"error": "Invalid response from job service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Fetch resumes for the job from Resume Service
        resumes_response = requests.get(f'http://localhost:8001/api/resumes/?job_id={job_id}')
        logger.info(f"Resume Service Response: {resumes_response.status_code}, {resumes_response.text}")

        if resumes_response.status_code != 200:
            return Response({"error": "Failed to fetch resumes"}, status=resumes_response.status_code)

        try:
            resumes = resumes_response.json()
        except ValueError:
            return Response({"error": "Invalid response from resume service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        scored_resumes = []
        explanations = []
        for resume in resumes:
            resume_text = resume.get('text', '')
            resume_id = resume.get('id', '')  # Ensure to get the correct key for resume ID
            if resume_text and resume_id:  # Only score resumes that have text and a valid ID
                try:
                    score, explanation = self.score_resume(job_description, resume_text)
                    scored_resumes.append((resume_id, score))
                    explanations.append((resume_id, explanation))
                except Exception as e:
                    logger.error(f"Error scoring resume: {str(e)}")

        # Sort resumes by score and select top candidates
        scored_resumes.sort(key=lambda x: x[1], reverse=True)
        top_candidates = scored_resumes[:num_candidates]

        # Store shortlisted candidates
        shortlisted_candidates = []
        for resume_id, score in top_candidates:
            candidate = ShortlistedCandidate.objects.create(job_id=job_id, resume_id=resume_id, score=score)
            candidate.explanation = next(expl for res_id, expl in explanations if res_id == resume_id)
            candidate.save()
            shortlisted_candidates.append(candidate)

        candidate_serializer = ShortlistedCandidateSerializer(shortlisted_candidates, many=True)
        return Response(candidate_serializer.data, status=status.HTTP_200_OK)

    def score_resume(self, job_description, resume_text):
        openai.api_key = "sk-proj-hl4IaWp6z7qOOnCCeMMOT3BlbkFJD2c3IjQ4IJirknLiXn8v" # Retrieve the API key from settings

        prompt = f"""
        Evaluate the resume based on the job description.
    
        Job Description:
        {job_description}
    
        Resume:
        {resume_text}
    
        Provide a final score (0-100) and a brief explanation for the score. Format the response as 'Final Score: X' followed by the explanation.
        """

        logger.info(f"OpenAI Prompt: {prompt}")

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced recruiter."},
                    {"role": "user", "content": prompt}
                ]
            )
            logger.info(f"OpenAI Response: {response}")

            if not response or 'choices' not in response or not response['choices']:
                raise ValueError("Invalid response structure from OpenAI API")

            content = response['choices'][0]['message']['content'].strip()
            logger.info(f"Response Content: {content}")

            # Extract score and explanations
            lines = content.split('\n')
            score_line = lines[0].split(":")

            # Improved score extraction logic
            if len(score_line) < 2 or not score_line[0].strip().lower().startswith("final score"):
                raise ValueError("Score line format is invalid")

            score = float(score_line[1].strip())
            explanation = "\n".join(lines[1:]).strip()

            return score, explanation
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
