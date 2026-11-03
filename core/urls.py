from django.urls import path
from core import views
from core.api import views as api_views

urlpatterns = [
    # Public & Auth
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile & Onboarding
    path('onboarding/', views.onboarding_view, name='onboarding'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Generator & Content Ideas
    path('generator/', views.generator_view, name='generator'),
    path('ideas/save/<int:idea_id>/', views.save_idea_view, name='save_idea'),
    path('ideas/favorite/<int:idea_id>/', views.toggle_favorite_view, name='toggle_favorite'),
    path('ideas/saved/', views.saved_ideas_view, name='saved_ideas'),
    path('ideas/<int:idea_id>/', views.idea_detail_view, name='idea_detail'),
    path('ideas/<int:idea_id>/edit/', views.idea_edit_view, name='idea_edit'),
    path('ideas/<int:idea_id>/delete/', views.idea_delete_view, name='idea_delete'),
    path('ideas/<int:idea_id>/schedule/', views.schedule_idea_view, name='schedule_idea'),

    # Content Planner
    path('planner/', views.planner_view, name='planner'),
    path('planner/<int:entry_id>/edit/', views.planner_edit_view, name='planner_edit'),
    path('planner/<int:entry_id>/delete/', views.planner_delete_view, name='planner_delete'),

    # Studio & Inspiration
    path('captions/', views.caption_studio_view, name='caption_studio'),
    path('inspiration/', views.inspiration_view, name='inspiration'),

    # FAQ & Support
    path('faq/', views.faq_view, name='faq'),
    path('support/', views.tickets_view, name='tickets'),
    path('support/<str:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),

    # REST APIs
    path('api/faqs/', api_views.FAQListAPIView.as_view(), name='api_faqs'),
    path('api/error-codes/', api_views.ErrorCodeListAPIView.as_view(), name='api_error_codes'),
    path('api/assistant/chat/', api_views.AssistantChatAPIView.as_view(), name='api_assistant_chat'),
    path('api/assistant/feedback/', api_views.AssistantFeedbackAPIView.as_view(), name='api_assistant_feedback'),

    # Health Check Endpoint
    path('health/', api_views.HealthCheckAPIView.as_view(), name='health_check'),
]
