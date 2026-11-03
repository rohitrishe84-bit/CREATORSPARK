from django.core.management.base import BaseCommand
from core.models import FAQ

FAQS_DATA = [
    {
        "question": "What is CreatorSpark?",
        "answer": "CreatorSpark is an all-in-one Instagram content planning, idea-generation, and workflow platform designed for influencers, UGC creators, beginner creators, and small businesses looking to grow consistently on Instagram.",
        "category": "General",
        "order": 1,
    },
    {
        "question": "How do I create an account?",
        "answer": "Click on 'Register' in the top navigation, enter a username, email address, and secure password, then complete the brief creator onboarding to customize your niche and target audience.",
        "category": "Account",
        "order": 2,
    },
    {
        "question": "How does the content idea generator work?",
        "answer": "Navigate to 'Idea Generator', select your niche, content goal (e.g. increase reach, boost engagement), format (Reels, Carousels, Stories), and tone. Our structured generation engine outputs a complete concept including title, hooks, slide/frame outline, visual direction, caption, hashtags, and filming tips.",
        "category": "Generator",
        "order": 3,
    },
    {
        "question": "How do I choose or update my Instagram niche?",
        "answer": "You can select your primary niche during onboarding or anytime by going to 'Profile Settings'. Choosing a specific niche helps the generator tailor relevant hooks, vocabulary, and community hashtags.",
        "category": "Profile",
        "order": 4,
    },
    {
        "question": "How do I generate high-converting Reel ideas?",
        "answer": "In the Idea Generator, choose 'Reels (Short-form Video)' as your format and select 'Increase Reach & Discovery' or 'Boost Engagement'. The engine emphasizes 3-second visual hooks, pacing transitions, audio suggestions, and clear text overlays.",
        "category": "Generator",
        "order": 5,
    },
    {
        "question": "How do I build educational Carousel posts?",
        "answer": "Choose 'Carousels' as your format and 'Educate & Add Value' or 'Drive Saves & Shares' as your goal. You will receive a slide-by-slide blueprint: Slide 1 (Curiosity hook), Slides 2-5 (Core lessons), Slide 6 (Summary), and Slide 7 (Save/Share Call-to-Action).",
        "category": "Generator",
        "order": 6,
    },
    {
        "question": "How do I save and favorite generated ideas?",
        "answer": "When viewing any generated idea, click 'Save to Library'. You can also click the heart icon to mark it as a Favorite. All saved concepts are accessible anytime under the 'Saved Ideas' tab.",
        "category": "Content Management",
        "order": 7,
    },
    {
        "question": "Can I edit a saved idea after saving?",
        "answer": "Yes. In 'Saved Ideas', click 'View Details' on any idea card and then select 'Edit'. You can refine the title, hook, caption, hashtags, or outline to match your unique brand voice.",
        "category": "Content Management",
        "order": 8,
    },
    {
        "question": "How do I use the Content Planner & Calendar?",
        "answer": "Go to 'Content Planner' to schedule posts for upcoming dates. You can create a new post from scratch or schedule a saved idea directly. Track workflow stages with statuses: Idea, Planned, In Progress, Ready to Publish, and Published.",
        "category": "Planner",
        "order": 9,
    },
    {
        "question": "How does the Caption & Hashtag Studio work?",
        "answer": "Open 'Caption Studio', enter a topic or keyword, choose your tone and caption length, and generate ready-to-copy captions with categorized hashtags divided into Broad, Niche, Community, and Topic groups.",
        "category": "Studio",
        "order": 10,
    },
    {
        "question": "Are hashtag suggestions guaranteed to increase reach?",
        "answer": "No algorithm or hashtag guarantees reach or engagement. CreatorSpark provides relevant, categorized hashtags based on current niche practices to help categorize your content, but high quality content and audience engagement remain the primary drivers.",
        "category": "Studio",
        "order": 11,
    },
    {
        "question": "How do I update my profile and target audience?",
        "answer": "Click your username in the navigation menu and select 'Profile Settings'. Here you can update your display name, Instagram handle, bio, niche, target audience description, and preferred format.",
        "category": "Profile",
        "order": 12,
    },
    {
        "question": "How does the Assistant Chat Widget work?",
        "answer": "The floating chat widget in the bottom-right corner provides instant answers to CreatorSpark platform questions, explains error codes (e.g. CS-AUTH-001), and can escalate unresolved questions directly into a support ticket.",
        "category": "Assistant",
        "order": 13,
    },
    {
        "question": "How do I submit and track support tickets?",
        "answer": "You can ask the Assistant to open a ticket when an issue arises, or navigate to 'Support' in the navigation bar. You can view all your open tickets, inspect status updates (Open, In Progress, Resolved), and view staff resolution notes.",
        "category": "Support",
        "order": 14,
    },
    {
        "question": "Does CreatorSpark post directly to Instagram?",
        "answer": "CreatorSpark is currently a dedicated content strategy, idea generation, and planning platform. It does not automatically post or publish directly to your Instagram account without your manual action, avoiding unauthorized API risks.",
        "category": "General",
        "order": 15,
    },
]

class Command(BaseCommand):
    help = "Seeds standard SQL FAQ knowledge base entries idempotently."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in FAQS_DATA:
            faq, created = FAQ.objects.update_or_create(
                question=item["question"],
                defaults={
                    "answer": item["answer"],
                    "category": item["category"],
                    "order": item["order"],
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded FAQs: {created_count} created, {updated_count} updated. Total: {FAQ.objects.count()}"
            )
        )
