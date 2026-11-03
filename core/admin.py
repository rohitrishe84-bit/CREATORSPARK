from django.contrib import admin
from core.models import (
    CreatorProfile, ContentIdea, PlannerEntry, FAQ, ErrorCode, SupportTicket
)

@admin.register(CreatorProfile)
class CreatorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'display_name', 'niche', 'experience_level', 'onboarding_completed', 'created_at']
    list_filter = ['niche', 'experience_level', 'onboarding_completed']
    search_fields = ['user__username', 'display_name', 'instagram_handle', 'bio']


@admin.register(ContentIdea)
class ContentIdeaAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'niche', 'format_type', 'content_goal', 'is_saved', 'is_favorite', 'created_at']
    list_filter = ['niche', 'format_type', 'content_goal', 'is_saved', 'is_favorite']
    search_fields = ['title', 'hook', 'main_concept', 'caption', 'hashtags']


@admin.register(PlannerEntry)
class PlannerEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'scheduled_date', 'scheduled_time', 'format_type', 'status']
    list_filter = ['status', 'format_type', 'scheduled_date']
    search_fields = ['title', 'notes']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'updated_at']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']


@admin.register(ErrorCode)
class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'severity', 'is_active', 'updated_at']
    list_filter = ['category', 'severity', 'is_active']
    search_fields = ['code', 'title', 'description', 'possible_causes', 'recommended_solution']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'subject', 'user', 'priority', 'status', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['ticket_id', 'subject', 'description', 'guest_email', 'guest_name', 'related_error_code']
    readonly_fields = ['ticket_id', 'created_at', 'updated_at']
