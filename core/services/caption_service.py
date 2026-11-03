import re
from typing import Dict, Any, List

NICHE_HASHTAGS = {
    'beauty': {
        'niche': ['#BeautyHacks', '#MakeupTutorial', '#GlowyMakeup', '#BeautyCommunity', '#DrugstoreBeauty'],
        'community': ['#BeautyCreators', '#MakeupAddicts', '#CleanBeautySquad', '#GlowUpDaily'],
    },
    'skincare': {
        'niche': ['#SkincareRoutine', '#SkinBarrier', '#HealthySkinGoals', '#DermatologyTips', '#ClearSkinTips'],
        'community': ['#SkincareAddict', '#SkincareCommunity', '#SkinFirst', '#GlassSkinGoals'],
    },
    'fashion': {
        'niche': ['#OOTDInspo', '#CapsuleWardrobe', '#OutfitIdeas', '#StyleGuide', '#EverydayFashion'],
        'community': ['#FashionCreators', '#WearThisNext', '#StreetwearDaily', '#MinimalistStyle'],
    },
    'lifestyle': {
        'niche': ['#DailyVlog', '#SundayReset', '#MorningRoutine', '#CozyVibes', '#MindfulLiving'],
        'community': ['#LifestyleCreators', '#SlowLiving', '#AestheticDaily', '#ThatGirlAesthetic'],
    },
    'fitness': {
        'niche': ['#WorkoutInspo', '#GymTips', '#FormCheck', '#HealthyHabits', '#FitnessRoutine'],
        'community': ['#FitnessCommunity', '#GymRatLife', '#StrengthTraining', '#WellnessJourney'],
    },
    'food': {
        'niche': ['#EasyRecipes', '#QuickMeals', '#FoodInspo', '#HomeCooking', '#MealPrepSunday'],
        'community': ['#FoodieGram', '#RecipeCreators', '#CookWithMe', '#DeliciousEats'],
    },
    'travel': {
        'niche': ['#TravelTips', '#HiddenGems', '#BudgetTravel', '#SoloTraveler', '#TravelItinerary'],
        'community': ['#TravelCreators', '#WanderlustVibes', '#TravelAddicts', '#ExploreMore'],
    },
    'education': {
        'niche': ['#LearnDaily', '#ProductivityHacks', '#StudySmart', '#KnowledgeDrop', '#SkillBuilding'],
        'community': ['#EduCreators', '#LifelongLearning', '#GrowthMindset', '#BookSmart'],
    },
    'technology': {
        'niche': ['#TechHacks', '#AITools', '#ProductivityTech', '#DeskSetup', '#WorkflowAutomation'],
        'community': ['#TechCreators', '#FutureOfTech', '#DeveloperLife', '#TechCommunity'],
    },
    'business': {
        'niche': ['#SmallBizTips', '#EntrepreneurLife', '#MarketingStrategy', '#FreelanceLife', '#RevenueGrowth'],
        'community': ['#FoundersClub', '#Solopreneur', '#CreativeBusiness', '#SmallBizCommunity'],
    },
    'ugc': {
        'niche': ['#UGCCreator', '#ContentCreator', '#BrandDeals', '#UGCCommunity', '#MicroInfluencer'],
        'community': ['#UGCJourney', '#UGCFilmingTips', '#PaidCollabs', '#CreatorEconomy'],
    },
    'default': {
        'niche': ['#ContentStrategy', '#InstagramGrowth', '#CreativeLife', '#ContentCreation', '#DailyInspo'],
        'community': ['#CreatorCommunity', '#CreatorsOfInstagram', '#BuildInPublic', '#OnlineBrand'],
    }
}

BROAD_HASHTAGS = [
    '#ContentCreator', '#InstagramTips', '#CreatorEconomy', '#ViralContent',
    '#PostOfTheDay', '#TrendingNow', '#ExplorePage'
]


class CaptionService:
    """
    Dedicated service for generating customized Instagram captions and
    categorized hashtags (Broad, Niche, Community, Topic).
    Supports multiple styles, lengths, emoji density, and targeted calls to action.
    """

    @classmethod
    def clean_topic_tags(cls, topic: str) -> List[str]:
        words = re.findall(r'[A-Za-z0-9]+', topic)
        if not words:
            return ['#TrendingTopic']
        tags = []
        combined = '#' + ''.join(w.capitalize() for w in words)
        tags.append(combined)
        for w in words[:3]:
            if len(w) > 2:
                tags.append(f"#{w.capitalize()}")
        return list(dict.fromkeys(tags))

    @classmethod
    def generate_hashtags(cls, topic: str, niche: str) -> Dict[str, Any]:
        niche_key = niche.lower() if niche else 'default'
        niche_data = NICHE_HASHTAGS.get(niche_key, NICHE_HASHTAGS['default'])

        broad = BROAD_HASHTAGS[:5]
        niche_tags = niche_data['niche']
        community_tags = niche_data['community']
        topic_tags = cls.clean_topic_tags(topic)

        all_unique = list(dict.fromkeys(broad + niche_tags + community_tags + topic_tags))

        return {
            'broad': broad,
            'niche': niche_tags,
            'community': community_tags,
            'topic': topic_tags,
            'all_tags': all_unique,
            'formatted_string': ' '.join(all_unique)
        }

    @classmethod
    def generate_caption(
        cls,
        topic: str,
        niche: str,
        tone: str = 'friendly',
        length: str = 'medium',
        style: str = 'conversational',
        emoji_level: str = 'moderate',
        cta_type: str = 'save'
    ) -> Dict[str, str]:
        topic_clean = topic.strip() if topic else "this creator strategy"
        niche_clean = niche.capitalize() if niche else "Content Creation"

        # Emojis helper
        em_spark = " ✨" if emoji_level != 'none' else ""
        em_pin = " 📌" if emoji_level != 'none' else ""
        em_arrow = " 👇" if emoji_level != 'none' else ""
        em_chat = " 💬" if emoji_level != 'none' else ""

        # Call to Action selection
        if cta_type == 'comment':
            cta = f"Have you experienced this with {topic_clean}? Drop your thoughts below!{em_chat}"
        elif cta_type == 'share':
            cta = f"Send this to a creator friend who needs to hear this today!{em_spark}"
        elif cta_type == 'link_bio':
            cta = f"Tap the link in my bio to get the full step-by-step breakdown! 🔗"
        elif cta_type == 'dm':
            cta = f"Send me a DM with '{topic_clean.upper()}' and I'll send over the complete template!"
        else: # save
            cta = f"Save this checklist so you can reference it before your next post!{em_pin}"

        # Generate based on Style
        if style == 'storytelling':
            hook = f"I used to believe that succeeding with {topic_clean} required hours of overthinking.{em_arrow}"
            if length == 'short':
                body = f"The moment I simplified my process in {niche_clean}, everything changed. Focus on one core takeaway per post and let consistency do the heavy lifting."
            else:
                body = (
                    f"When I first started in {niche_clean}, I made every mistake in the book when approaching {topic_clean}.\n\n"
                    f"I chased complex frameworks, bought tools I didn't need, and worried about perfection.\n\n"
                    f"Here is what actually moved the needle:\n"
                    f"1. Clarity: Know the exact question your viewer has.\n"
                    f"2. Simplicity: Remove the fluff; deliver the payoff in the first 15 seconds.\n"
                    f"3. Repetition: The best creators aren't reinventing the wheel—they're executing proven fundamentals consistently."
                )
        elif style == 'contrarian':
            hook = f"Unpopular opinion: Most creator advice about {topic_clean} is completely backwards.{em_arrow}"
            body = (
                f"Everyone tells you to post 5 times a day or follow every micro-trend.\n\n"
                f"In reality? A single well-researched, high-retention post on {topic_clean} will outperform 10 rushed pieces of content.\n\n"
                f"Quality builds trust. Trust drives saves and shares."
            )
        elif style == 'how_to':
            hook = f"How to master {topic_clean} in 3 actionable steps (save this!):{em_pin}"
            body = (
                f"Step 1: Define your target viewer's #1 pain point.\n"
                f"Step 2: Present the simple transformation with proof or real-life examples.\n"
                f"Step 3: Conclude with a clear next step rather than a vague conclusion."
            )
        elif style == 'quick_tips':
            hook = f"3 quick reminders about {topic_clean} before you plan your next post:{em_arrow}"
            body = (
                f"• Hook in the first 2 lines before the fold.\n"
                f"• One idea per post—don't overwhelm your audience.\n"
                f"• High contrast visuals keep viewers from scrolling past."
            )
        else: # conversational / standard
            if length == 'short':
                hook = f"The biggest mistake creators make with {topic_clean}{em_arrow}"
                body = f"Stop overcomplicating it. Simplify your delivery, test small variations, and pay attention to what your audience actually saves."
            elif length == 'long':
                hook = f"Let's have an honest conversation about {topic_clean} in {niche_clean}."
                body = (
                    f"When it comes to {topic_clean}, so many creators give up right before they find their rhythm.\n\n"
                    f"The secret isn't magic—it's having a reliable structure:\n"
                    f"1. Capture curiosity instantly.\n"
                    f"2. Deliver clear, actionable value.\n"
                    f"3. Make it easy to save or share.\n\n"
                    f"Keep experimenting until you find the angle that resonates with your community."
                )
            else: # medium
                hook = f"Bookmark this before you plan your next post on {topic_clean}!{em_spark}"
                body = (
                    f"Here is a simple framework to make {topic_clean} work for you:\n"
                    f"• Hook with curiosity in the first 2 lines.\n"
                    f"• Keep your core explanation concise and relatable.\n"
                    f"• Give a clear next step instead of a vague takeaway."
                )

        full_caption = f"{hook}\n\n{body}\n\n{cta}"

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
            'full_caption': full_caption,
            'style': style,
            'length': length,
        }
