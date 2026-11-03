import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
import requests

from core.models import (
    CreatorProfile, ContentIdea, PlannerEntry, FAQ, ErrorCode, SupportTicket
)
from core.services.generator_service import GeneratorService
from core.services.caption_service import CaptionService
from core.services.pexels_service import PexelsService, FALLBACK_CURATED_PHOTOS
from core.services.assistant_service import AssistantService
from core.services.mongo_service import MongoService


class CreatorSparkCoreTests(TestCase):
    """Automated tests for core user features, authentication, onboarding, and dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testcreator',
            email='test@creatorspark.io',
            password='Password123!'
        )
        self.profile = CreatorProfile.objects.create(
            user=self.user,
            display_name='Test Influencer',
            instagram_handle='@testcreator',
            niche='skincare',
            target_audience='People wanting clear skin',
            onboarding_completed=True
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Never Run Out of")
        self.assertContains(response, "CreatorSpark")

    def test_about_page_loads(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technical Architecture")

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(CreatorProfile.objects.filter(user__username='newuser').exists())

    def test_duplicate_email_registration_fails(self):
        response = self.client.post(reverse('register'), {
            'username': 'duplicateemail',
            'email': 'test@creatorspark.io',
            'password': 'SecurePassword123!',
            'confirm_password': 'SecurePassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_login_and_logout(self):
        login_res = self.client.post(reverse('login'), {
            'username': 'testcreator',
            'password': 'Password123!'
        })
        self.assertEqual(login_res.status_code, 302)
        self.assertRedirects(login_res, reverse('dashboard'))

        logout_res = self.client.get(reverse('logout'))
        self.assertEqual(logout_res.status_code, 302)
        self.assertRedirects(logout_res, reverse('home'))

    def test_onboarding_submission(self):
        self.client.login(username='testcreator', password='Password123!')
        response = self.client.post(reverse('onboarding'), {
            'display_name': 'Glow Guru',
            'instagram_handle': '@glowguru',
            'niche': 'beauty',
            'target_audience': 'Beauty lovers looking for easy glam',
            'content_goals': 'engagement',
            'preferred_formats': 'reels',
            'preferred_tone': 'aesthetic',
            'experience_level': 'growing',
            'bio': 'Sharing daily beauty hacks.'
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.niche, 'beauty')
        self.assertTrue(self.profile.onboarding_completed)

    def test_dashboard_metrics(self):
        self.client.login(username='testcreator', password='Password123!')
        # Create a saved idea and planner entry
        ContentIdea.objects.create(
            user=self.user,
            title='Test Skincare Reel',
            niche='skincare',
            format_type='reels',
            content_goal='reach',
            main_concept='Barrier repair steps',
            hook='Stop washing your face in hot water',
            objective='Educate',
            content_outline='Outline steps',
            visual_direction='Soft bathroom light',
            caption='Full caption',
            hashtags='#Skincare',
            call_to_action='Save this',
            is_saved=True,
            is_favorite=True
        )
        PlannerEntry.objects.create(
            user=self.user,
            title='Test Planned Post',
            format_type='reels',
            scheduled_date=date.today() + timedelta(days=2),
            status='planned'
        )

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Skincare Reel")
        self.assertContains(response, "Test Planned Post")


class ContentGeneratorAndPlannerTests(TestCase):
    """Automated tests for idea generation engine, saved library, and planner."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='creator_alex', password='Password123!')
        CreatorProfile.objects.create(user=self.user, niche='fitness')
        self.client.login(username='creator_alex', password='Password123!')

    def test_generator_service_structured_output(self):
        payload = {
            'niche': 'fitness',
            'format_type': 'reels',
            'content_goal': 'reach',
            'tone': 'informative',
            'topic': 'squat form check',
            'target_audience': 'Gym beginners'
        }
        res = GeneratorService.generate_idea(payload)

        self.assertIn('title', res)
        self.assertIn('hook', res)
        self.assertIn('content_outline', res)
        self.assertIn('visual_direction', res)
        self.assertIn('caption', res)
        self.assertIn('hashtags', res)
        self.assertIn('call_to_action', res)
        self.assertIn('difficulty_level', res)
        self.assertIn('estimated_effort', res)
        self.assertIn('filming_editing_tips', res)
        self.assertIn('squat form check', res['title'].lower())

    def test_generator_view_creates_idea(self):
        response = self.client.post(reverse('generator'), {
            'niche': 'fitness',
            'format_type': 'carousels',
            'content_goal': 'educate',
            'tone': 'informative',
            'topic': 'deadlift cues',
            'target_audience': 'Strength beginners'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContentIdea.objects.filter(user=self.user, niche='fitness').exists())

    def test_save_and_favorite_idea(self):
        idea = ContentIdea.objects.create(
            user=self.user,
            title='Unsaved Idea',
            niche='fitness',
            format_type='reels',
            content_goal='reach',
            main_concept='Concept',
            hook='Hook line',
            objective='Objective',
            content_outline='Outline',
            visual_direction='Visuals',
            caption='Caption',
            hashtags='#Fitness',
            call_to_action='CTA',
            is_saved=False
        )

        # Save
        save_res = self.client.get(reverse('save_idea', args=[idea.id]))
        self.assertEqual(save_res.status_code, 302)
        idea.refresh_from_db()
        self.assertTrue(idea.is_saved)

        # Favorite
        fav_res = self.client.get(reverse('toggle_favorite', args=[idea.id]))
        self.assertEqual(fav_res.status_code, 302)
        idea.refresh_from_db()
        self.assertTrue(idea.is_favorite)

    def test_user_cannot_access_other_users_idea(self):
        other_user = User.objects.create_user(username='other_user', password='Password123!')
        private_idea = ContentIdea.objects.create(
            user=other_user,
            title='Private Concept',
            niche='business',
            format_type='reels',
            content_goal='leads',
            main_concept='Concept',
            hook='Hook',
            objective='Obj',
            content_outline='Outline',
            visual_direction='Visual',
            caption='Caption',
            hashtags='#Biz',
            call_to_action='CTA',
            is_saved=True
        )

        response = self.client.get(reverse('idea_detail', args=[private_idea.id]))
        self.assertEqual(response.status_code, 404)

    def test_caption_and_hashtag_service(self):
        cap = CaptionService.generate_caption('sunscreen comparison', 'skincare', 'friendly', 'short')
        self.assertIn('hook', cap)
        self.assertIn('full_caption', cap)

        tags = CaptionService.generate_hashtags('sunscreen comparison', 'skincare')
        self.assertTrue(len(tags['broad']) > 0)
        self.assertTrue(len(tags['niche']) > 0)
        self.assertTrue(len(tags['community']) > 0)
        self.assertTrue(len(tags['topic']) > 0)

    def test_planner_crud(self):
        create_res = self.client.post(reverse('planner'), {
            'title': 'Weekly Workout Reel',
            'format_type': 'reels',
            'scheduled_date': str(date.today()),
            'status': 'planned',
            'notes': 'Filming on turf'
        })
        self.assertEqual(create_res.status_code, 302)
        entry = PlannerEntry.objects.get(user=self.user, title='Weekly Workout Reel')

        # Edit
        edit_res = self.client.post(reverse('planner_edit', args=[entry.id]), {
            'title': 'Updated Workout Reel',
            'format_type': 'reels',
            'scheduled_date': str(date.today()),
            'status': 'in_progress',
            'notes': 'Finished filming'
        })
        self.assertEqual(edit_res.status_code, 302)
        entry.refresh_from_db()
        self.assertEqual(entry.title, 'Updated Workout Reel')
        self.assertEqual(entry.status, 'in_progress')

        # Delete
        del_res = self.client.post(reverse('planner_delete', args=[entry.id]))
        self.assertEqual(del_res.status_code, 302)
        self.assertFalse(PlannerEntry.objects.filter(id=entry.id).exists())

    def test_generator_with_additional_instructions(self):
        """Test generator service and view incorporate creative focus instructions."""
        self.client.login(username='testcreator', password='Password123!')
        response = self.client.post(reverse('generator'), {
            'niche': 'fitness',
            'format_type': 'reels',
            'content_goal': 'saves_shares',
            'target_audience': 'Busy office workers',
            'tone': 'informative',
            'topic': 'Desk posture fix',
            'additional_instructions': 'Include 3 specific seated stretches with 30s timers.',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Desk posture fix")
        self.assertContains(response, "Structured Strategy Engine (Rule-based)")
        self.assertContains(response, "Open in Caption Studio")

        idea = ContentIdea.objects.filter(user=self.user, title__icontains='Desk posture fix').first()
        if not idea:
            idea = ContentIdea.objects.filter(user=self.user).latest('created_at')
        self.assertIn("Include 3 specific seated stretches", idea.main_concept)

    def test_caption_studio_styles_and_direct_save(self):
        """Test caption studio generation options and saving directly to ContentIdea library."""
        # Test generation with contrarian style and custom CTA
        cap = CaptionService.generate_caption(
            topic='Intermittent Fasting',
            niche='fitness',
            tone='bold',
            length='short',
            style='contrarian',
            emoji_level='minimal',
            cta_type='comment'
        )
        self.assertIn('Unpopular opinion', cap['hook'])
        self.assertIn('Intermittent Fasting', cap['full_caption'])
        self.assertIn('Drop your thoughts below', cap['cta'])

        # Test POST directly saving caption into user's saved library
        self.client.login(username='testcreator', password='Password123!')
        response = self.client.post(reverse('caption_studio'), {
            'topic': 'Morning Routine',
            'niche': 'lifestyle',
            'caption_text': 'Here is the 5am routine that doubled my productivity.',
            'hook_text': 'Stop waking up at 5am without this habit.',
            'hashtags_text': '#morningroutine #productivity #creatorlife',
        })
        self.assertEqual(response.status_code, 302)
        saved_idea = ContentIdea.objects.filter(user=self.user, title__icontains='Morning Routine').first()
        self.assertIsNotNone(saved_idea)
        self.assertTrue(saved_idea.is_saved)
        self.assertIn('Morning Routine', saved_idea.title)
        self.assertEqual(saved_idea.caption, 'Here is the 5am routine that doubled my productivity.')

    def test_planner_monthly_calendar_grid(self):
        """Test planner monthly calendar calculations, navigation, and week matrix."""
        self.client.login(username='testcreator', password='Password123!')
        
        # Create an entry on 2026-11-15
        test_date = date(2026, 11, 15)
        PlannerEntry.objects.create(
            user=self.user,
            title='November Strategy Reel',
            format_type='reels',
            scheduled_date=test_date,
            status='planned'
        )

        response = self.client.get(reverse('planner'), {'view': 'calendar', 'year': 2026, 'month': 11})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view_mode'], 'calendar')
        self.assertEqual(response.context['current_month_name'], 'November')
        self.assertEqual(response.context['current_year'], 2026)
        self.assertEqual(response.context['prev_month'], 10)
        self.assertEqual(response.context['next_month'], 12)
        
        # Verify calendar weeks matrix contains the entry
        weeks = response.context['calendar_weeks']
        self.assertTrue(len(weeks) >= 4)
        found_entry = False
        for week in weeks:
            for day in week:
                if day['date'] == test_date:
                    self.assertEqual(len(day['entries']), 1)
                    self.assertEqual(day['entries'][0].title, 'November Strategy Reel')
                    found_entry = True
        self.assertTrue(found_entry)
        self.assertContains(response, "November Strategy Reel")

    def test_ticket_security_and_authorization(self):
        """Verify strict authorization on support tickets (prevent ID enumeration)."""
        # 1. Unauthenticated guest submits ticket
        guest_client = Client()
        post_res = guest_client.post(reverse('tickets'), {
            'guest_name': 'Guest Tester',
            'guest_email': 'guest@example.com',
            'subject': 'Guest issue query',
            'description': 'Cannot load the preview.',
            'priority': 'Low'
        })
        self.assertEqual(post_res.status_code, 302)
        ticket = SupportTicket.objects.get(guest_email='guest@example.com')

        # The guest client has it in session, can view it
        view_res = guest_client.get(reverse('ticket_detail', args=[ticket.ticket_id]))
        self.assertEqual(view_res.status_code, 200)
        self.assertContains(view_res, ticket.ticket_id)

        # 2. An unrelated unauthenticated client cannot view the guest ticket
        unrelated_client = Client()
        forbidden_res = unrelated_client.get(reverse('ticket_detail', args=[ticket.ticket_id]))
        self.assertEqual(forbidden_res.status_code, 403)

        # 3. Authenticated user cannot view another user's ticket
        user_b = User.objects.create_user(username='userb', password='Password123!')
        user_b_ticket = SupportTicket.objects.create(
            user=user_b,
            subject='User B private ticket',
            description='Private information'
        )

        self.client.login(username='testcreator', password='Password123!')
        res_forbidden = self.client.get(reverse('ticket_detail', args=[user_b_ticket.ticket_id]))
        self.assertEqual(res_forbidden.status_code, 403)

        # 4. Staff user CAN view any ticket
        staff_user = User.objects.create_superuser(username='adminstaff', email='admin@creatorspark.io', password='Password123!')
        self.client.login(username='adminstaff', password='Password123!')
        staff_res = self.client.get(reverse('ticket_detail', args=[user_b_ticket.ticket_id]))
        self.assertEqual(staff_res.status_code, 200)


class TechnicalRequirementsTests(TestCase):
    """Automated tests for the 12 technical requirements: FAQ API, ErrorCodes, Assistant, Tickets, Health."""

    def setUp(self):
        self.client = Client()

        # Seed test FAQ
        self.faq = FAQ.objects.create(
            question="How do I save an idea in CreatorSpark?",
            answer="Click the 'Save to Library' button on any generated concept.",
            category="Generator",
            order=1,
            is_active=True
        )
        self.faq2 = FAQ.objects.create(
            question="What is CreatorSpark?",
            answer="CreatorSpark is an Instagram content planning platform.",
            category="General",
            order=2,
            is_active=True
        )

        # Seed test ErrorCodes
        self.err_auth = ErrorCode.objects.create(
            code="CS-AUTH-001",
            title="Authentication Required",
            description="The requested action requires you to be logged into an account.",
            possible_causes="Session expired or accessing private route while logged out.",
            recommended_solution="Log in at /login/.",
            category="Authentication",
            severity="Medium",
            is_active=True
        )
        self.err_data = ErrorCode.objects.create(
            code="CS-DATA-001",
            title="Saved Idea Not Found",
            description="Resource not found in library.",
            possible_causes="Deleted or invalid ID.",
            recommended_solution="Check your saved library.",
            category="Data",
            severity="Low",
            is_active=True
        )

    def test_faq_api_endpoint(self):
        response = self.client.get(reverse('api_faqs'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('count', data)
        self.assertIn('categories', data)
        self.assertGreaterEqual(data['count'], 2)

        # Category filter test
        filtered_res = self.client.get(reverse('api_faqs') + '?category=Generator')
        self.assertEqual(filtered_res.status_code, 200)
        filtered_data = filtered_res.json()
        self.assertEqual(filtered_data['count'], 1)
        self.assertEqual(filtered_data['results'][0]['category'], 'Generator')

    def test_error_code_api_endpoint(self):
        response = self.client.get(reverse('api_error_codes'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('count', data)
        self.assertGreaterEqual(data['count'], 2)

    def test_assistant_explains_error_code(self):
        payload = {
            'message': 'What does error CS-AUTH-001 mean?',
            'conversation_id': 'test-session-1'
        }
        response = self.client.post(
            reverse('api_assistant_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'error_code')
        self.assertIn('CS-AUTH-001', data['reply'])
        self.assertIn('Authentication Required', data['reply'])

    def test_assistant_answers_faq(self):
        payload = {
            'message': 'How do I save an idea?',
            'conversation_id': 'test-session-2'
        }
        response = self.client.post(
            reverse('api_assistant_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'faq')
        self.assertIn('Save to Library', data['reply'])

    def test_assistant_unknown_question_offers_ticket(self):
        payload = {
            'message': 'xyz obscure non-existent question that matches nothing',
            'conversation_id': 'test-session-3'
        }
        response = self.client.post(
            reverse('api_assistant_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'unknown')
        self.assertTrue(data['can_create_ticket'])
        self.assertIn('support ticket', data['reply'].lower())

    def test_assistant_ticket_confirmation_action(self):
        payload = {
            'conversation_id': 'test-session-4',
            'action': 'confirm_ticket',
            'ticket_subject': 'Cannot export video',
            'ticket_desc': 'The generator outline does not save.'
        }
        response = self.client.post(
            reverse('api_assistant_chat'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'ticket_created')
        self.assertTrue(data['ticket_id'].startswith('TK-'))
        self.assertTrue(SupportTicket.objects.filter(ticket_id=data['ticket_id']).exists())

    def test_support_ticket_crud(self):
        # Create ticket via standard support form
        response = self.client.post(reverse('tickets'), {
            'guest_name': 'Reporter',
            'guest_email': 'reporter@example.com',
            'subject': 'Bug in caption copying',
            'description': 'Clipboard button did not change state.',
            'priority': 'Medium',
            'related_error_code': 'CS-FORM-001'
        })
        self.assertEqual(response.status_code, 302)
        ticket = SupportTicket.objects.get(subject='Bug in caption copying')
        self.assertTrue(ticket.ticket_id.startswith('TK-'))

        # Detail view
        detail_res = self.client.get(reverse('ticket_detail', args=[ticket.ticket_id]))
        self.assertEqual(detail_res.status_code, 200)
        self.assertContains(detail_res, ticket.ticket_id)

    def test_health_check_endpoint(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['database'], 'connected')
        self.assertIn('mongodb', data)

    def test_request_logging_middleware_and_correlation_id(self):
        response = self.client.get(reverse('home'), HTTP_X_REQUEST_ID='custom-cid-1234')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Request-ID'], 'custom-cid-1234')

    def test_pexels_service_fallback(self):
        # With no key configured or on exception, service returns curated fallback
        with patch.object(PexelsService, 'search_photos', wraps=PexelsService.search_photos):
            res = PexelsService.search_photos(query='lifestyle')
            self.assertIn('photos', res)
            self.assertTrue(len(res['photos']) > 0)
            self.assertIn(res['source'], ['curated_fallback', 'pexels_api'])

    def test_pexels_service_timeout_handling(self):
        with patch('requests.get', side_effect=requests.exceptions.Timeout("Connection timed out")):
            with patch('django.conf.settings.PEXELS_API_KEY', 'dummy-key'):
                res = PexelsService.search_photos(query='fashion')
                self.assertTrue(res['is_fallback'])
                self.assertIn('timed out', res['message'].lower())
                self.assertTrue(len(res['photos']) > 0)

    def test_mongodb_graceful_offline_handling(self):
        # When MongoDB URI is not set, methods return False / empty without raising exception
        with patch('django.conf.settings.MONGODB_URI', ''):
            self.assertFalse(MongoService.is_available())
            self.assertFalse(MongoService.save_message('c1', 'user', 'hello'))
            self.assertEqual(MongoService.get_conversation_history('c1'), [])
            self.assertFalse(MongoService.save_feedback('c1', 5, 'Great'))

    def test_custom_404_page(self):
        response = self.client.get('/this-path-definitely-does-not-exist-404/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "404 — Page Not Found", status_code=404)
        self.assertContains(response, "CS-DATA-001", status_code=404)
        self.assertContains(response, "Ask Assistant", status_code=404)


