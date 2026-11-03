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
    def generate_caption(cls, topic: str, niche: str, tone: str = 'friendly', length: str = 'medium') -> Dict[str, str]:
        topic_clean = topic.strip() if topic else "this creator strategy"
        niche_clean = niche.capitalize() if niche else "Content Creation"

        if length == 'short':
            hook = f"The biggest mistake people make with {topic_clean} 👇"
            body = f"Stop doing what everyone else is doing. Simplify your process, test consistently, and let the results speak."
            cta = "Double-tap if you agree and save this for later! 📌"
        elif length == 'long':
            hook = f"Let's have an honest conversation about {topic_clean} in {niche_clean}."
            body = (
                f"When I first started focusing on {topic_clean}, I assumed the only way to win was grinding 24/7 or having fancy gear.\n\n"
                f"The truth? It all comes down to 3 fundamentals:\n"
                f"1. Clarity: Knowing exactly what problem you solve.\n"
                f"2. Retention: Keeping your viewer engaged from frame one.\n"
                f"3. Value: Leaving the viewer with something actionable they can use today.\n\n"
                f"Save yourself weeks of trial and error by sticking to these 3 pillars."
            )
            cta = "Tell me in the comments: what is your #1 struggle with this right now? Let's troubleshoot together. 💬"
        else: # medium
            hook = f"Bookmark this before you plan your next post on {topic_clean}! ⚡"
            body = (
                f"Here is a simple framework to make {topic_clean} work for you:\n"
                f"• Hook with curiosity in the first 2 lines.\n"
                f"• Keep your core explanation concise and relatable.\n"
                f"• Give a clear next step instead of a vague takeaway."
            )
            cta = "Drop a ✨ in the comments if this was helpful, and share it to your stories!"

        full_caption = f"{hook}\n\n{body}\n\n{cta}"

        return {
            'hook': hook,
            'body': body,
            'cta': cta,
            'full_caption': full_caption,
        }
