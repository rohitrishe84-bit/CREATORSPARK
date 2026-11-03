import json
import calendar
from collections import defaultdict
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.db.models import Count, Q

from core.models import (
    CreatorProfile, ContentIdea, PlannerEntry, FAQ, ErrorCode, SupportTicket
)
from core.forms import (
    UserRegistrationForm, CreatorOnboardingForm, CreatorProfileForm,
    IdeaGeneratorForm, ContentIdeaEditForm, PlannerEntryForm, SupportTicketForm
)
from core.services.generator_service import GeneratorService
from core.services.caption_service import CaptionService
from core.services.pexels_service import PexelsService


# -------------------------------------------------------------
# Public & Authentication Views
# -------------------------------------------------------------

def home_view(request):
    """Modern SaaS landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/home.html')


def about_view(request):
    """About CreatorSpark, mission, and architecture."""
    return render(request, 'core/about.html')


def register_view(request):
    """User registration with automatic profile creation and onboarding redirect."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Ensure profile exists
            CreatorProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome to CreatorSpark, {user.username}! Let's set up your creator profile.")
            return redirect('onboarding')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """User authentication view."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. (Error Ref: CS-AUTH-001)")
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# -------------------------------------------------------------
# Onboarding & Creator Profile Views
# -------------------------------------------------------------

@login_required
def onboarding_view(request):
    """First-time onboarding to select niche, goals, and audience."""
    profile, _ = CreatorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CreatorOnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            prof.onboarding_completed = True
            prof.save()
            messages.success(request, "Profile configured! Let's generate your first Instagram content idea.")
            return redirect('generator')
    else:
        form = CreatorOnboardingForm(instance=profile)

    return render(request, 'core/onboarding.html', {'form': form})


@login_required
def profile_view(request):
    """View and update creator preferences."""
    profile, _ = CreatorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CreatorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your creator profile has been updated.")
            return redirect('profile')
        else:
            messages.error(request, "Please check the form inputs.")
    else:
        form = CreatorProfileForm(instance=profile)

    return render(request, 'core/profile.html', {'form': form, 'profile': profile})


# -------------------------------------------------------------
# Creator Dashboard
# -------------------------------------------------------------

@login_required
def dashboard_view(request):
    """Creator central hub with metrics, recent ideas, and upcoming schedule."""
    profile, _ = CreatorProfile.objects.get_or_create(user=request.user)

    total_generated = ContentIdea.objects.filter(user=request.user).count()
    saved_ideas_count = ContentIdea.objects.filter(user=request.user, is_saved=True).count()
    favorite_count = ContentIdea.objects.filter(user=request.user, is_favorite=True).count()
    planned_count = PlannerEntry.objects.filter(user=request.user, status__in=['planned', 'in_progress', 'ready']).count()
    published_count = PlannerEntry.objects.filter(user=request.user, status='published').count()

    recent_ideas = ContentIdea.objects.filter(user=request.user)[:5]
    upcoming_posts = PlannerEntry.objects.filter(
        user=request.user,
        scheduled_date__gte=date.today()
    ).order_by('scheduled_date', 'scheduled_time')[:5]

    # Format distribution for Chart.js
    format_counts = (
        ContentIdea.objects.filter(user=request.user)
        .values('format_type')
        .annotate(total=Count('id'))
    )
    chart_labels = [fc['format_type'].capitalize() for fc in format_counts]
    chart_data = [fc['total'] for fc in format_counts]

    context = {
        'profile': profile,
        'total_generated': total_generated,
        'saved_ideas_count': saved_ideas_count,
        'favorite_count': favorite_count,
        'planned_count': planned_count,
        'published_count': published_count,
        'recent_ideas': recent_ideas,
        'upcoming_posts': upcoming_posts,
        'chart_labels_json': json.dumps(chart_labels or ['Reels', 'Carousels', 'Stories']),
        'chart_data_json': json.dumps(chart_data or [0, 0, 0]),
    }
    return render(request, 'core/dashboard.html', context)


# -------------------------------------------------------------
# Content Idea Generator & Management
# -------------------------------------------------------------

@login_required
def generator_view(request):
    """Instagram Content Idea Generator."""
    profile, _ = CreatorProfile.objects.get_or_create(user=request.user)
    generated_idea = None

    if request.method == 'POST':
        form = IdeaGeneratorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not data.get('target_audience'):
                data['target_audience'] = profile.target_audience

            idea_dict = GeneratorService.generate_idea(data)

            # Create ephemeral or stored record for the user
            idea_obj = ContentIdea.objects.create(
                user=request.user,
                title=idea_dict['title'],
                niche=idea_dict['niche'],
                format_type=idea_dict['format_type'],
                content_goal=idea_dict['content_goal'],
                target_audience=idea_dict['target_audience'],
                tone=idea_dict['tone'],
                difficulty_level=idea_dict['difficulty_level'],
                estimated_effort=idea_dict['estimated_effort'],
                main_concept=idea_dict['main_concept'],
                hook=idea_dict['hook'],
                objective=idea_dict['objective'],
                content_outline=idea_dict['content_outline'],
                visual_direction=idea_dict['visual_direction'],
                caption=idea_dict['caption'],
                hashtags=idea_dict['hashtags'],
                call_to_action=idea_dict['call_to_action'],
                filming_editing_tips=idea_dict['filming_editing_tips'],
                is_saved=False,
            )
            generated_idea = idea_obj
            messages.success(request, f"Generated: \"{idea_obj.title}\"")
        else:
            messages.error(request, "Please review form fields. (Ref: CS-FORM-001)")
    else:
        # Pre-populate with profile defaults
        initial_data = {
            'niche': profile.niche,
            'format_type': profile.preferred_formats or 'reels',
            'content_goal': profile.content_goals or 'reach',
            'tone': profile.preferred_tone or 'relatable',
            'target_audience': profile.target_audience,
        }
        form = IdeaGeneratorForm(initial=initial_data)

    return render(request, 'core/generator.html', {
        'form': form,
        'generated_idea': generated_idea,
        'profile': profile,
    })


@login_required
def save_idea_view(request, idea_id):
    """Mark an idea as saved to user library."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)
    idea.is_saved = True
    idea.save()
    messages.success(request, f"Saved \"{idea.title}\" to your library!")
    return redirect('saved_ideas')


@login_required
def toggle_favorite_view(request, idea_id):
    """Toggle favourite status."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)
    idea.is_favorite = not idea.is_favorite
    idea.save()
    status_str = "added to" if idea.is_favorite else "removed from"
    messages.info(request, f"Idea {status_str} favorites.")
    return redirect(request.META.get('HTTP_REFERER', 'saved_ideas'))


@login_required
def saved_ideas_view(request):
    """View and search user's saved library."""
    queryset = ContentIdea.objects.filter(user=request.user, is_saved=True)

    # Filtering
    niche = request.GET.get('niche')
    format_type = request.GET.get('format_type')
    goal = request.GET.get('goal')
    search = request.GET.get('q')
    favorites_only = request.GET.get('favorites')

    if niche:
        queryset = queryset.filter(niche__iexact=niche)
    if format_type:
        queryset = queryset.filter(format_type__iexact=format_type)
    if goal:
        queryset = queryset.filter(content_goal__iexact=goal)
    if favorites_only:
        queryset = queryset.filter(is_favorite=True)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(hook__icontains=search) |
            Q(caption__icontains=search)
        )

    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/saved_ideas.html', {
        'page_obj': page_obj,
        'total_saved': queryset.count(),
        'selected_niche': niche or '',
        'selected_format': format_type or '',
        'selected_goal': goal or '',
        'search_query': search or '',
        'favorites_only': bool(favorites_only),
    })


@login_required
def idea_detail_view(request, idea_id):
    """View complete idea outline and tips."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)
    return render(request, 'core/idea_detail.html', {'idea': idea})


@login_required
def idea_edit_view(request, idea_id):
    """Edit saved idea details."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)

    if request.method == 'POST':
        form = ContentIdeaEditForm(request.POST, instance=idea)
        if form.is_valid():
            form.save()
            messages.success(request, "Idea updated successfully.")
            return redirect('idea_detail', idea_id=idea.id)
    else:
        form = ContentIdeaEditForm(instance=idea)

    return render(request, 'core/idea_edit.html', {'form': form, 'idea': idea})


@login_required
def idea_delete_view(request, idea_id):
    """Delete a saved idea."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)
    if request.method == 'POST':
        idea.delete()
        messages.success(request, "Idea deleted from library.")
        return redirect('saved_ideas')
    return render(request, 'core/idea_confirm_delete.html', {'idea': idea})


@login_required
def schedule_idea_view(request, idea_id):
    """Quick schedule a saved idea into the Content Planner."""
    idea = get_object_or_404(ContentIdea, id=idea_id, user=request.user)

    if request.method == 'POST':
        scheduled_date_str = request.POST.get('scheduled_date')
        if not scheduled_date_str:
            scheduled_date = date.today() + timedelta(days=1)
        else:
            scheduled_date = scheduled_date_str

        if not idea.is_saved:
            idea.is_saved = True
            idea.save()

        entry = PlannerEntry.objects.create(
            user=request.user,
            idea=idea,
            title=idea.title,
            format_type=idea.format_type,
            scheduled_date=scheduled_date,
            status='planned',
            notes=f"Hook: {idea.hook[:120]}...",
        )
        messages.success(request, f"Scheduled \"{entry.title}\" for {entry.scheduled_date}!")
        return redirect('planner')

    return render(request, 'core/schedule_idea.html', {'idea': idea, 'tomorrow': date.today() + timedelta(days=1)})


# -------------------------------------------------------------
# Content Planner & Calendar Views
# -------------------------------------------------------------

@login_required
def planner_view(request):
    """Instagram Content Planner (List & Calendar Overview)."""
    status_filter = request.GET.get('status')
    view_mode = request.GET.get('view', 'list')

    entries = PlannerEntry.objects.filter(user=request.user)

    if status_filter:
        entries = entries.filter(status=status_filter)

    # Form for adding a new scheduled post
    if request.method == 'POST':
        form = PlannerEntryForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, f"Scheduled post \"{post.title}\" for {post.scheduled_date}.")
            return redirect(f"{request.path}?view={view_mode}")
        else:
            messages.error(request, "Please check post scheduling details. (Ref: CS-PLAN-001)")
    else:
        # Pre-populate date if provided in query params (e.g. clicked on calendar day)
        initial_date = request.GET.get('date', date.today().isoformat())
        try:
            date.fromisoformat(initial_date)
        except (ValueError, TypeError):
            initial_date = date.today().isoformat()
        form = PlannerEntryForm(initial={'scheduled_date': initial_date})

    upcoming = entries.filter(scheduled_date__gte=date.today()).order_by('scheduled_date', 'scheduled_time')
    past_entries = entries.filter(scheduled_date__lt=date.today()).order_by('-scheduled_date')

    # Calendar Month Grid Data Calculation
    today = date.today()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        if month < 1 or month > 12:
            year, month = today.year, today.month
    except (ValueError, TypeError):
        year, month = today.year, today.month

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    month_dates = cal.monthdatescalendar(year, month)

    start_grid_date = month_dates[0][0]
    end_grid_date = month_dates[-1][-1]
    grid_entries = entries.filter(
        scheduled_date__gte=start_grid_date,
        scheduled_date__lte=end_grid_date
    ).order_by('scheduled_time', 'id')

    entries_by_date = defaultdict(list)
    for entry in grid_entries:
        entries_by_date[entry.scheduled_date].append(entry)

    calendar_weeks = []
    for week in month_dates:
        week_days = []
        for d in week:
            week_days.append({
                'date': d,
                'iso_date': d.isoformat(),
                'day_num': d.day,
                'is_current_month': (d.month == month),
                'is_today': (d == today),
                'entries': entries_by_date[d],
                'count': len(entries_by_date[d]),
            })
        calendar_weeks.append(week_days)

    context = {
        'form': form,
        'upcoming': upcoming,
        'past_entries': past_entries,
        'status_filter': status_filter or '',
        'view_mode': view_mode,
        'total_entries': entries.count(),
        'calendar_weeks': calendar_weeks,
        'current_year': year,
        'current_month': month,
        'current_month_name': calendar.month_name[month],
        'prev_year': prev_year,
        'prev_month': prev_month,
        'prev_month_name': calendar.month_name[prev_month],
        'next_year': next_year,
        'next_month': next_month,
        'next_month_name': calendar.month_name[next_month],
        'today': today,
    }
    return render(request, 'core/planner.html', context)


@login_required
def planner_edit_view(request, entry_id):
    """Edit planned post."""
    entry = get_object_or_404(PlannerEntry, id=entry_id, user=request.user)

    if request.method == 'POST':
        form = PlannerEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Scheduled post updated.")
            return redirect('planner')
    else:
        form = PlannerEntryForm(instance=entry)

    return render(request, 'core/planner_edit.html', {'form': form, 'entry': entry})


@login_required
def planner_delete_view(request, entry_id):
    """Delete planned post."""
    entry = get_object_or_404(PlannerEntry, id=entry_id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Post removed from schedule.")
        return redirect('planner')
    return render(request, 'core/planner_confirm_delete.html', {'entry': entry})


# -------------------------------------------------------------
# Caption & Hashtag Studio
# -------------------------------------------------------------

def caption_studio_view(request):
    """Dedicated studio for crafting hooks, captions, and categorized hashtags."""
    caption_result = None
    hashtag_result = None
    topic = request.GET.get('topic', '').strip()
    niche = request.GET.get('niche', 'lifestyle')
    tone = request.GET.get('tone', 'friendly')
    length = request.GET.get('length', 'medium')
    style = request.GET.get('style', 'conversational')
    emoji_level = request.GET.get('emoji_level', 'moderate')
    cta_type = request.GET.get('cta_type', 'save')

    # Handle saving caption as a saved idea
    if request.method == 'POST' and request.user.is_authenticated:
        caption_text = request.POST.get('caption_text', '')
        hook_text = request.POST.get('hook_text', '')
        hashtags_text = request.POST.get('hashtags_text', '')
        topic_post = request.POST.get('topic') or "Instagram Caption"
        niche_post = request.POST.get('niche') or "lifestyle"

        if caption_text:
            idea = ContentIdea.objects.create(
                user=request.user,
                title=f"Caption: {topic_post.title()}",
                niche=niche_post,
                format_type='reels',
                content_goal='engagement',
                main_concept=f"Created in Caption Studio for '{topic_post}'.",
                hook=hook_text or f"Hook for {topic_post}",
                objective="Deliver engaging caption copy and hashtag groups.",
                content_outline="• Visual text overlay hook\n• Main message breakdown\n• Explicit call to action",
                visual_direction="High readability, neutral background with clear focus.",
                caption=caption_text,
                hashtags=hashtags_text,
                call_to_action="Follow and save for more",
                is_saved=True,
            )
            messages.success(request, f"Saved \"{idea.title}\" to your content library!")
            return redirect('idea_detail', idea_id=idea.id)

    if topic:
        caption_result = CaptionService.generate_caption(
            topic=topic,
            niche=niche,
            tone=tone,
            length=length,
            style=style,
            emoji_level=emoji_level,
            cta_type=cta_type
        )
        hashtag_result = CaptionService.generate_hashtags(topic, niche)

    return render(request, 'core/caption_studio.html', {
        'caption_result': caption_result,
        'hashtag_result': hashtag_result,
        'topic': topic,
        'niche': niche,
        'tone': tone,
        'length': length,
        'style': style,
        'emoji_level': emoji_level,
        'cta_type': cta_type,
    })


# -------------------------------------------------------------
# Visual Inspiration Gallery (Pexels API)
# -------------------------------------------------------------

def inspiration_view(request):
    """Inspiration gallery with Pexels API + curated fallback."""
    query = request.GET.get('q', 'creator aesthetic')
    result = PexelsService.search_photos(query=query, per_page=12)

    return render(request, 'core/inspiration.html', {
        'result': result,
        'query': query,
    })


# -------------------------------------------------------------
# FAQ Page (Fetches from /api/faqs/)
# -------------------------------------------------------------

def faq_view(request):
    """FAQ page populated dynamically via the SQL API."""
    return render(request, 'core/faq.html')


# -------------------------------------------------------------
# Support Tickets (CRUD)
# -------------------------------------------------------------

def tickets_view(request):
    """List user tickets and provide ticket submission form."""
    if request.user.is_authenticated:
        tickets = SupportTicket.objects.filter(user=request.user)
    else:
        tickets = SupportTicket.objects.none()

    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                ticket.user = request.user
                if not ticket.guest_name:
                    ticket.guest_name = request.user.username
                if not ticket.guest_email:
                    ticket.guest_email = request.user.email
            ticket.save()

            # Record guest ticket in session for authorization
            submitted = request.session.get('submitted_tickets', [])
            if ticket.ticket_id not in submitted:
                submitted.append(ticket.ticket_id)
                request.session['submitted_tickets'] = submitted

            messages.success(request, f"Ticket #{ticket.ticket_id} submitted! We will respond shortly.")
            return redirect('ticket_detail', ticket_id=ticket.ticket_id)
        else:
            messages.error(request, "Please correct the errors in the ticket form. (Ref: CS-FORM-001)")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {'guest_name': request.user.username, 'guest_email': request.user.email}
        form = SupportTicketForm(initial=initial)

    return render(request, 'core/tickets.html', {
        'tickets': tickets,
        'form': form,
    })


def ticket_detail_view(request, ticket_id):
    """View single ticket status and staff notes with strict authorization."""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    # Permission check:
    # 1. Staff can view any ticket.
    # 2. Registered owner can view their ticket.
    # 3. Submitter who holds the ticket_id in session can view it.
    # Otherwise, reject to prevent guest ticket enumeration.
    if request.user.is_authenticated:
        if request.user.is_staff:
            pass
        elif ticket.user and ticket.user != request.user:
            return HttpResponseForbidden("Access Denied: You do not have permission to view this ticket. (Ref: CS-AUTH-002)")
        elif ticket.user is None:
            session_tickets = request.session.get('submitted_tickets', [])
            if ticket.ticket_id not in session_tickets and ticket.guest_email != request.user.email:
                return HttpResponseForbidden("Access Denied: You do not have permission to view this guest ticket. (Ref: CS-AUTH-002)")
    else:
        if ticket.user is not None:
            return HttpResponseForbidden("Authentication Required to view this ticket. (Ref: CS-AUTH-001)")
        session_tickets = request.session.get('submitted_tickets', [])
        if ticket.ticket_id not in session_tickets:
            return HttpResponseForbidden("Access Denied: You do not have permission to view this guest ticket. (Ref: CS-AUTH-002)")

    return render(request, 'core/ticket_detail.html', {'ticket': ticket})


# -------------------------------------------------------------
# Custom Error Handlers (404 and 500)
# -------------------------------------------------------------

def custom_404(request, exception=None):
    """Custom 404 page with Ask Assistant integration."""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 page with Ask Assistant integration."""
    return render(request, '500.html', status=500)
