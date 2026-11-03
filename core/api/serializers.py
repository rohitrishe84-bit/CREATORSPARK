from rest_framework import serializers
from core.models import FAQ, ErrorCode, SupportTicket, ContentIdea, PlannerEntry

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'created_at', 'updated_at']

class ErrorCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorCode
        fields = ['id', 'code', 'title', 'description', 'possible_causes', 'recommended_solution', 'category', 'severity']

class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = ['ticket_id', 'subject', 'description', 'related_error_code', 'priority', 'status', 'resolution_notes', 'created_at', 'updated_at']
        read_only_fields = ['ticket_id', 'status', 'resolution_notes', 'created_at', 'updated_at']

class ContentIdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentIdea
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']

class PlannerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannerEntry
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
