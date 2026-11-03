import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

NICHE_CHOICES = [
    ('beauty', 'Beauty'),
    ('skincare', 'Skincare'),
    ('fashion', 'Fashion'),
    ('lifestyle', 'Lifestyle'),
    ('travel', 'Travel'),
    ('food', 'Food & Cooking'),
    ('fitness', 'Fitness & Wellness'),
    ('education', 'Education & Tips'),
    ('technology', 'Technology & AI'),
    ('personal_development', 'Personal Development'),
    ('business', 'Small Business & Marketing'),
    ('photography', 'Photography & Videography'),
    ('ugc', 'UGC & Content Creation'),
    ('other', 'Other'),
]

FORMAT_CHOICES = [
    ('reels', 'Reels (Short-form Video)'),
    ('carousels', 'Carousels (Swipe Post)'),
    ('single_image', 'Single Image Post'),
    ('stories', 'Stories (24h Interactive)'),
    ('educational', 'Educational Deep Dive'),
    ('product_review', 'Product Review / Showcase'),
    ('tutorial', 'How-To / Step-by-Step Tutorial'),
    ('behind_the_scenes', 'Behind-the-Scenes (BTS)'),
    ('before_after', 'Before & After Concept'),
    ('ugc_style', 'UGC Style Authentic Testimonial'),
]

GOAL_CHOICES = [
    ('reach', 'Increase Reach & Discovery'),
    ('engagement', 'Boost Engagement (Comments/Likes)'),
    ('trust', 'Build Trust & Credibility'),
    ('educate', 'Educate & Add Value'),
    ('promote', 'Promote Product / Offer'),
    ('leads', 'Generate Leads & Inquiries'),
    ('brand', 'Build Personal Brand Identity'),
    ('saves_shares', 'Drive Saves & Shares'),
    ('community', 'Grow Loyal Community'),
]

TONE_CHOICES = [
    ('aesthetic', 'Aesthetic & Inspiring'),
    ('professional', 'Professional & Authoritative'),
    ('friendly', 'Friendly & Warm'),
    ('funny', 'Humorous & Entertaining'),
    ('informative', 'Informative & Actionable'),
    ('relatable', 'Relatable & Casual'),
    ('minimal', 'Minimalist & Direct'),
    ('storytelling', 'Narrative & Storytelling'),
    ('persuasive', 'Persuasive & High-Converting'),
]

EXPERIENCE_CHOICES = [
    ('beginner', 'Beginner (<1,000 followers)'),
    ('growing', 'Growing Creator (1k - 10k)'),
    ('established', 'Established Creator (10k - 50k)'),
    ('pro', 'Professional / Agency (50k+)'),
]

PLANNER_STATUS_CHOICES = [
    ('idea', 'Idea Draft'),
    ('planned', 'Planned'),
    ('in_progress', 'In Progress'),
    ('ready', 'Ready to Publish'),
    ('published', 'Published (Recorded)'),
]

TICKET_STATUS_CHOICES = [
    ('Open', 'Open'),
    ('In Progress', 'In Progress'),
    ('Resolved', 'Resolved'),
    ('Closed', 'Closed'),
]

PRIORITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Urgent', 'Urgent'),
]

SEVERITY_CHOICES = [
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Critical', 'Critical'),
]


class CreatorProfile(models.Model):
    """Stores creator preferences, niche settings, and onboarding state."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    instagram_handle = models.CharField(max_length=60, blank=True)
    niche = models.CharField(max_length=50, choices=NICHE_CHOICES, default='beauty')
    target_audience = models.CharField(max_length=150, blank=True, help_text="e.g. Gen-Z women wanting clear glass skin")
    content_goals = models.CharField(max_length=100, blank=True, default='reach')
    preferred_formats = models.CharField(max_length=100, blank=True, default='reels')
    preferred_tone = models.CharField(max_length=50, blank=True, default='relatable')
    experience_level = models.CharField(max_length=30, choices=EXPERIENCE_CHOICES, default='beginner')
    bio = models.TextField(blank=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.display_name or self.user.username} ({self.get_niche_display()})"


class ContentIdea(models.Model):
    """Stores generated and user-saved Instagram content concepts."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ideas')
    title = models.CharField(max_length=255)
    niche = models.CharField(max_length=60)
    format_type = models.CharField(max_length=60)
    content_goal = models.CharField(max_length=100)
    target_audience = models.CharField(max_length=150, blank=True)
    tone = models.CharField(max_length=50, blank=True)
    difficulty_level = models.CharField(max_length=30, default='Beginner')
    estimated_effort = models.CharField(max_length=50, default='30 mins')

    main_concept = models.TextField()
    hook = models.TextField(help_text="Attention-grabbing opening line or on-screen text")
    objective = models.TextField()
    content_outline = models.TextField(help_text="Step-by-step frames or slide progression")
    visual_direction = models.TextField(help_text="Lighting, camera angle, aesthetic notes")
    caption = models.TextField()
    hashtags = models.TextField()
    call_to_action = models.CharField(max_length=255)
    filming_editing_tips = models.TextField(blank=True)

    is_saved = models.BooleanField(default=False, db_index=True)
    is_favorite = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.format_type}]"


class PlannerEntry(models.Model):
    """Stores planned Instagram posts and calendar schedule items."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planner_entries')
    idea = models.ForeignKey(ContentIdea, on_delete=models.SET_NULL, null=True, blank=True, related_name='scheduled_posts')
    title = models.CharField(max_length=255)
    format_type = models.CharField(max_length=60, default='reels')
    scheduled_date = models.DateField(db_index=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=PLANNER_STATUS_CHOICES, default='planned', db_index=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date', 'scheduled_time']

    def __str__(self):
        return f"{self.scheduled_date} - {self.title} ({self.status})"


class FAQ(models.Model):
    """SQL-backed FAQ system for CreatorSpark product knowledge."""
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=60, default='General', db_index=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class ErrorCode(models.Model):
    """SQL-backed catalog of standard CreatorSpark error codes."""
    code = models.CharField(max_length=30, unique=True, db_index=True)
    title = models.CharField(max_length=150)
    description = models.TextField()
    possible_causes = models.TextField()
    recommended_solution = models.TextField()
    category = models.CharField(max_length=60, default='General', db_index=True)
    severity = models.CharField(max_length=30, choices=SEVERITY_CHOICES, default='Medium')
    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code}: {self.title}"


class SupportTicket(models.Model):
    """SQL-backed customer support and error escalation ticket system."""
    ticket_id = models.CharField(max_length=32, unique=True, db_index=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    guest_email = models.EmailField(blank=True)
    guest_name = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    related_error_code = models.CharField(max_length=30, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default='Open', db_index=True)
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate readable unique ticket ID like TK-XXXXXX
            random_part = uuid.uuid4().hex[:6].upper()
            self.ticket_id = f"TK-{random_part}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.ticket_id}] {self.subject} ({self.status})"
