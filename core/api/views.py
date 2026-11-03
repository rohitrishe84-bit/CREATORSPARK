import logging
from datetime import datetime, timezone
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from core.models import FAQ, ErrorCode, SupportTicket
from core.api.serializers import FAQSerializer, ErrorCodeSerializer, SupportTicketSerializer
from core.services.assistant_service import AssistantService
from core.services.mongo_service import MongoService

logger = logging.getLogger('creatorspark.api')

class FAQListAPIView(APIView):
    """
    GET /api/faqs/
    Retrieves active FAQ records.
    Supports ?category= filtering and search query ?q=.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        category = request.query_params.get('category', '').strip()
        search_query = request.query_params.get('q', '').strip()

        queryset = FAQ.objects.filter(is_active=True)

        if category and category.lower() != 'all':
            # Case-insensitive category match
            queryset = queryset.filter(category__iexact=category)

        if search_query:
            queryset = queryset.filter(question__icontains=search_query) | queryset.filter(answer__icontains=search_query)

        serializer = FAQSerializer(queryset, many=True)

        categories = list(FAQ.objects.filter(is_active=True).values_list('category', flat=True).distinct())

        return Response({
            'count': len(serializer.data),
            'categories': categories,
            'results': serializer.data
        }, status=status.HTTP_200_OK)


class ErrorCodeListAPIView(APIView):
    """
    GET /api/error-codes/
    Retrieves the standard catalog of active ErrorCodes.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = ErrorCode.objects.filter(is_active=True)
        serializer = ErrorCodeSerializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


class AssistantChatAPIView(APIView):
    """
    POST /api/assistant/chat/
    Accepts user question or confirmation payload and returns deterministic response.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', '').strip() or 'default-session'
        action = data.get('action')
        ticket_subject = data.get('ticket_subject')
        ticket_desc = data.get('ticket_desc')

        if not message and action != 'confirm_ticket':
            return Response(
                {'error': 'A message or actionable payload is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = AssistantService.process_message(
            message=message,
            conversation_id=conversation_id,
            user=request.user,
            action=action,
            ticket_subject=ticket_subject,
            ticket_desc=ticket_desc
        )

        return Response(result, status=status.HTTP_200_OK)


class AssistantFeedbackAPIView(APIView):
    """
    POST /api/assistant/feedback/
    Stores thumbs up/down rating or text feedback in MongoDB.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data or {}
        conversation_id = data.get('conversation_id', '').strip()
        rating = data.get('rating')
        feedback_text = data.get('feedback_text', '')
        user_id = request.user.id if request.user.is_authenticated else None

        if not conversation_id or rating is None:
            return Response(
                {'error': 'conversation_id and rating (1 or 5) are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        success = MongoService.save_feedback(
            conversation_id=conversation_id,
            rating=int(rating),
            feedback_text=feedback_text,
            user_id=user_id
        )

        return Response({
            'success': success,
            'message': 'Thank you for your feedback!' if success else 'Feedback logged locally (MongoDB storage offline).'
        }, status=status.HTTP_200_OK)


class HealthCheckAPIView(APIView):
    """
    GET /health/
    Requirement 11: Production-grade health check.
    Checks SQL database connection and MongoDB availability separately.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        now_iso = datetime.now(timezone.utc).isoformat()
        health_data = {
            "status": "ok",
            "application": "CreatorSpark",
            "version": "1.0.0",
            "timestamp": now_iso,
            "database": "unknown",
            "mongodb": "unknown",
        }

        # Check primary SQL database
        try:
            connection.ensure_connection()
            health_data["database"] = "connected"
        except Exception as e:
            logger.error(f"Health check failed on SQL database: {e}")
            health_data["database"] = "disconnected"
            health_data["status"] = "error"
            return Response(health_data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Check MongoDB if configured
        if settings.MONGODB_URI:
            if MongoService.is_available():
                health_data["mongodb"] = "connected"
            else:
                health_data["mongodb"] = "degraded"
        else:
            health_data["mongodb"] = "unconfigured"

        return Response(health_data, status=status.HTTP_200_OK)
