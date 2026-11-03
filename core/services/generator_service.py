import random
from typing import Dict, Any, List

NICHE_DETAILS = {
    'beauty': {
        'keywords': ['glowy makeup', 'clean girl look', 'drugstore dupes', 'long-lasting wear', 'beauty hacks', 'shade matching'],
        'audience': 'Beauty enthusiasts looking for easy routines and budget-friendly product hacks',
        'visuals': 'Warm natural window light, crisp macro close-ups of product textures, clean minimalist vanity backdrop.',
        'hashtags': '#BeautyHacks #MakeupTutorial #GlowySkin #BeautyTips #DrugstoreDupes #CreatorSpark',
        'tips': 'Use 4K 60fps for crisp skin texture. Avoid heavy filters; authenticity builds trust in beauty.',
    },
    'skincare': {
        'keywords': ['barrier repair', 'morning skincare', 'sunscreen test', 'retinol beginner guide', 'acne healing', 'double cleansing'],
        'audience': 'Skincare lovers seeking dermatologist-approved routines and ingredient breakdowns',
        'visuals': 'Bright diffuse bathroom lighting, slow-motion dropper shots, before-and-after texture swatches.',
        'hashtags': '#SkincareRoutine #SkinBarrier #HealthySkin #DermTips #ClearSkinJourney #SkincareCommunity',
        'tips': 'Show real skin texture under natural light. Clearly display ingredient percentages on screen.',
    },
    'fashion': {
        'keywords': ['capsule wardrobe', 'outfit transitions', 'styling 1 item 3 ways', 'thrift flip', 'color theory', 'seasonal essentials'],
        'audience': 'Style-conscious followers looking for wearable, effortless everyday outfit inspiration',
        'visuals': 'Full-length mirror angles, dynamic street-style walking shots, smooth snap transitions on the beat.',
        'hashtags': '#OOTD #StyleInspo #CapsuleWardrobe #OutfitIdeas #FashionTrends #StreetwearStyle',
        'tips': 'Time outfit changes strictly to trending rhythmic beats. Keep camera at chest level for natural proportions.',
    },
    'lifestyle': {
        'keywords': ['sunday reset', 'productive morning routine', 'workspace makeover', 'work-life balance', 'daily vlog', 'habit stacking'],
        'audience': 'Busy young adults seeking realistic productivity, wellness, and cozy aesthetic routines',
        'visuals': 'Cozy warm aesthetic, aesthetic b-roll of coffee brewing, gentle handheld camera motion.',
        'hashtags': '#SundayReset #MorningRoutine #AestheticVlog #ProductivityHacks #LifestyleCreator #CozyVibes',
        'tips': 'Use subtle ASMR audio (pages turning, kettle boiling, keyboard clicks) to increase watch time.',
    },
    'travel': {
        'keywords': ['hidden gems', 'budget travel guide', '48 hours in...', 'solo travel safety', 'packing light', 'what I spent in...'],
        'audience': 'Adventurers and travel dreamers searching for authentic local recommendations and budget itineraries',
        'visuals': 'Golden hour landscape drone b-roll, POV walking into scenic cafes, vivid color grading.',
        'hashtags': '#TravelTips #HiddenGems #SoloTravel #BudgetTravel #Wanderlust #TravelCreator',
        'tips': 'Drop the exact Google Maps coordinates or location names in the caption to maximize saves.',
    },
    'food': {
        'keywords': ['15-minute dinner', 'high-protein snacks', 'single-serve dessert', 'meal prep blueprint', 'budget grocery haul'],
        'audience': 'Foodies and busy individuals wanting mouth-watering, reproducible recipes with minimal cleanup',
        'visuals': 'Overhead cutting-board angle, sizzling pan close-up, steam rising, mouth-watering cheese-pull finale.',
        'hashtags': '#EasyRecipes #QuickMeals #FoodieGram #MealPrep #HomeCooking #RecipeOfTheDay',
        'tips': 'Put the complete ingredients list in the pinned comment or caption so viewers immediately save the post.',
    },
    'fitness': {
        'keywords': ['form check mistakes', 'at-home workout', 'glute activation', 'fat loss myths', 'progressive overload', 'pre-workout meal'],
        'audience': 'Fitness beginners and gym-goers wanting evidence-based form corrections and sustainable progress',
        'visuals': 'Side-profile full-body view, split-screen (Right vs Wrong form), red and green visual markers.',
        'hashtags': '#FitnessMotivation #FormCheck #WorkoutRoutine #GymTips #HealthyHabits #FitnessJourney',
        'tips': 'Highlight the exact muscle group working with a subtle colored overlay on the video.',
    },
    'education': {
        'keywords': ['cheat sheets', '3 mistakes beginner make', 'step-by-step breakdown', 'free tools nobody talks about', 'study frameworks'],
        'audience': 'Curious learners wanting condensed, actionable industry knowledge without fluff',
        'visuals': 'Clean contrast slides, bold sans-serif typography, subtle animated highlight markers.',
        'hashtags': '#LearnOnInstagram #KnowledgeDrop #SkillBuilding #ProductivityTools #EducationalContent',
        'tips': 'Keep each slide or tip under 12 words so users can read it comfortably in 3 seconds.',
    },
    'technology': {
        'keywords': ['AI tools for productivity', 'iPhone hidden features', 'desk setup upgrade', 'workflow automation', 'app breakdown'],
        'audience': 'Tech enthusiasts, freelancers, and remote workers looking for digital superpowers',
        'visuals': 'Sleek dark mode screen recordings, warm accent desk lights, crisp keyboard mechanical sounds.',
        'hashtags': '#TechHacks #AITools #ProductivityTech #DeskSetup #WorkflowTips #TechCreator',
        'tips': 'Zoom into screen menus so mobile viewers can clearly see the buttons and keystrokes.',
    },
    'personal_development': {
        'keywords': ['mindset shift', 'dopamine detox', 'overcoming imposter syndrome', 'morning journaling', 'hard truths in your 20s'],
        'audience': 'Growth-minded individuals striving for mental resilience and personal clarity',
        'visuals': 'Moody calm lighting, candid talking-head framing, gentle background music with voiceover clarity.',
        'hashtags': '#PersonalGrowth #MindsetShift #SelfImprovement #MentalClarity #CreatorMindset',
        'tips': 'Start with a vulnerable, emotionally resonant observation that challenges conventional wisdom.',
    },
    'business': {
        'keywords': ['how I landed my first client', 'pricing your services', 'email marketing template', 'organic growth funnel', 'case study'],
        'audience': 'Solopreneurs, small business founders, and freelancers scaling their revenue',
        'visuals': 'Clean whiteboards, analytical dashboard metrics, polished talking-head presentation.',
        'hashtags': '#SmallBizTips #Entrepreneurship #MarketingStrategy #FreelanceTips #BusinessGrowth',
        'tips': 'Back claims with specific numbers (e.g. \"How we reached 14,200 impressions without paid ads\").',
    },
    'photography': {
        'keywords': ['mobile camera settings', 'creative framing rules', 'free Lightroom presets', 'lighting on a budget', 'color grading guide'],
        'audience': 'Aspiring photographers and content creators looking to elevate their visual quality',
        'visuals': 'Dramatic before-and-after split screens, behind-the-scenes camera rig shots.',
        'hashtags': '#PhotographyTips #MobilePhotography #LightroomPresets #CameraHacks #VisualStorytelling',
        'tips': 'Show the unedited RAW photo first for 1 second, then snap to the finished edited masterpiece.',
    },
    'ugc': {
        'keywords': ['brand outreach email', 'filming aesthetic b-roll', 'hook rate optimization', 'portfolio builder', 'contract essentials'],
        'audience': 'UGC creators wanting paid brand sponsorships and higher conversion rates',
        'visuals': 'Unboxing hands-in-frame, genuine testimonial angle, crisp natural lighting.',
        'hashtags': '#UGCCreator #ContentCreator #BrandDeals #UGCCommunity #UGCFilmingTips #MicroInfluencer',
        'tips': 'Hold the product near your chest rather than right in front of your face to keep framing natural.',
    },
    'other': {
        'keywords': ['behind the process', '3 lessons I learned', 'frequently asked questions', 'my daily creative workflow'],
        'audience': 'General audience interested in creative lifestyle and practical tips',
        'visuals': 'Balanced composition, clean typography, engaging pacing.',
        'hashtags': '#ContentCreator #InstagramTips #DailyInspo #CreativeProcess #CreatorSpark',
        'tips': 'Focus on storytelling: Problem -> Discovery -> Transformation.',
    }
}

FORMAT_TEMPLATES = {
    'reels': {
        'outline_template': (
            "• [0:00 - 0:03] THE VISUAL HOOK: Rapid motion or curiosity statement on screen with dynamic audio.\n"
            "• [0:03 - 0:10] THE CONFLICT: Call out the common creator/viewer struggle directly.\n"
            "• [0:10 - 0:22] THE SOLUTION: Show the 3 rapid steps or technique in action with text markers.\n"
            "• [0:22 - 0:28] THE PAYOFF: Before/after transformation or final polished result.\n"
            "• [0:28 - 0:30] THE LOOP / CTA: Clear call to action on screen: 'Save this before your next shoot!'"
        ),
        'effort': '40-60 mins (Filming + Pacing Cuts)',
        'difficulty': 'Intermediate'
    },
    'carousels': {
        'outline_template': (
            "• Slide 1: BOLD COVER SLIDE with high-contrast text and curiosity hook.\n"
            "• Slide 2: THE PROBLEM breakdown (why traditional advice fails).\n"
            "• Slide 3: STEP 1 (The foundational action item with visual example).\n"
            "• Slide 4: STEP 2 (The overlooked pro tweak).\n"
            "• Slide 5: STEP 3 (The framework to avoid common mistakes).\n"
            "• Slide 6: QUICK SUMMARY CHEAT SHEET for instant screenshotting.\n"
            "• Slide 7: OUTRO SLIDE with 'Double tap & Save for later' CTA."
        ),
        'effort': '30-45 mins (Canva / Design Layout)',
        'difficulty': 'Beginner'
    },
    'single_image': {
        'outline_template': (
            "• Main Visual: High-impact hero shot or relatable quote graphic in 4:5 aspect ratio.\n"
            "• Visual Focus: Single clear focal point with negative space for text breathing room.\n"
            "• Micro-Hook: Bold 3-line overlay in the center.\n"
            "• Caption Synergy: Directing viewers from visual to the detailed story in the caption."
        ),
        'effort': '15-20 mins (Photography + Editing)',
        'difficulty': 'Beginner'
    },
    'stories': {
        'outline_template': (
            "• Story 1: Interactive Poll / Question Sticker ('Be honest, do you struggle with this?').\n"
            "• Story 2: Behind-the-scenes raw photo/video highlighting the problem.\n"
            "• Story 3: Quick 15s talking head sharing the solution.\n"
            "• Story 4: Link sticker or DM keyword trigger for resources."
        ),
        'effort': '10-15 mins (Real-time capture)',
        'difficulty': 'Beginner'
    },
    'educational': {
        'outline_template': (
            "• Section 1: Myth-busting opening that counters popular consensus.\n"
            "• Section 2: Anatomical breakdown of why the mistake happens.\n"
            "• Section 3: The 3-tier action framework with concrete examples.\n"
            "• Section 4: Resource checklist and downloadable/saveable guide."
        ),
        'effort': '45-60 mins (Research + Layout)',
        'difficulty': 'Intermediate'
    },
    'product_review': {
        'outline_template': (
            "• Shot 1: The product in action without revealing the brand name immediately (Curiosity).\n"
            "• Shot 2: Honest pros: What genuinely surprised you after 14 days of testing.\n"
            "• Shot 3: Honest cons: Who should NOT purchase this product.\n"
            "• Shot 4: Final verdict and who gets the most value."
        ),
        'effort': '35-50 mins (Testing + Swatches)',
        'difficulty': 'Beginner'
    },
    'tutorial': {
        'outline_template': (
            "• Step 0: The finished end-result shown for 1.5 seconds.\n"
            "• Step 1: Tool / Ingredient setup with on-screen annotations.\n"
            "• Step 2: The non-intuitive technique explained simply.\n"
            "• Step 3: Common pitfall to avoid.\n"
            "• Step 4: The final comparison."
        ),
        'effort': '30-45 mins (Step demonstration)',
        'difficulty': 'Intermediate'
    },
    'behind_the_scenes': {
        'outline_template': (
            "• Angle 1: Reality vs Instagram expectation.\n"
            "• Angle 2: The messy setup, lighting rigs, or bloopers.\n"
            "• Angle 3: The creative breakthrough moment.\n"
            "• Angle 4: The final published render."
        ),
        'effort': '20-30 mins (Casual recording)',
        'difficulty': 'Beginner'
    },
    'before_after': {
        'outline_template': (
            "• Frame 1: The underwhelming 'Before' with pain points highlighted.\n"
            "• Frame 2: The 1 pivot made to change the outcome.\n"
            "• Frame 3: The jaw-dropping 'After' transformation.\n"
            "• Frame 4: Checklist of what changed."
        ),
        'effort': '25-35 mins (Comparison framing)',
        'difficulty': 'Beginner'
    },
    'ugc_style': {
        'outline_template': (
            "• 0-2s: Relatable UGC hook ('I was skeptical until I tried this...').\n"
            "• 2-8s: Pain point in daily life.\n"
            "• 8-18s: Seamless product introduction & unboxing.\n"
            "• 18-26s: Demonstration of benefits in real life.\n"
            "• 26-30s: Honest recommendation & where to get it."
        ),
        'effort': '40-50 mins (Authentic phone video)',
        'difficulty': 'Beginner'
    }
}

HOOK_BANK = {
    'reach': [
        "Stop scrolling if you're still making this huge mistake in {topic}...",
        "Nobody is talking about this {topic} trick, but it changed everything for me.",
        "Here are 3 {niche} secrets the top 1% don't want you to know:",
        "If I had to start over in {niche} from scratch, here is exactly what I'd do:"
    ],
    'engagement': [
        "Unpopular opinion about {topic}: Be honest, do you agree or disagree?",
        "Drop a 'YES' below if you've ever dealt with this {topic} frustration...",
        "Which of these 2 approaches do you prefer? (Slide 1 or Slide 2?)",
        "Save this post right now because your future self is going to need it!"
    ],
    'educate': [
        "The complete 5-step blueprint to mastering {topic} (no gatekeeping):",
        "Stop wasting hours on {topic}. Here is the cheat code:",
        "How to get 10x better at {topic} in under 15 minutes a day.",
        "A breakdown of the exact framework I used to transform my {niche}."
    ],
    'promote': [
        "Why I finally decided to create the ultimate solution for {topic}:",
        "This one tool replaced 5 different apps in my {niche} workflow.",
        "The wait is over: here is how to level up your {topic} today."
    ],
    'saves_shares': [
        "Bookmark this {niche} checklist before you forget it!",
        "Send this to a friend who desperately needs to hear this today:",
        "The ultimate cheat sheet for {topic} that you will want to reference all week."
    ],
    'default': [
        "Here is the reality of {topic} that most creators overlook...",
        "3 simple shifts that transformed my results in {niche}:",
        "If you're struggling with {topic}, watch this until the end."
    ]
}


class GeneratorService:
    """
    Structured, template-based Instagram content generation service.
    Designed with a modular architecture so future LLMs (Gemini/OpenAI)
    can be plugged in smoothly without changing the consuming API.
    """

    @classmethod
    def generate_idea(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        niche = data.get('niche', 'lifestyle').lower()
        format_type = data.get('format_type', 'reels').lower()
        goal = data.get('content_goal', 'reach').lower()
        tone = data.get('tone', 'relatable')
        topic_input = (data.get('topic') or '').strip()
        audience_input = (data.get('target_audience') or '').strip()

        niche_info = NICHE_DETAILS.get(niche, NICHE_DETAILS['other'])
        format_info = FORMAT_TEMPLATES.get(format_type, FORMAT_TEMPLATES['reels'])

        # Determine topic
        if topic_input:
            topic = topic_input
        else:
            topic = random.choice(niche_info['keywords'])

        # Determine audience
        audience = audience_input or niche_info['audience']

        # Determine hook
        hooks_list = HOOK_BANK.get(goal, HOOK_BANK['default'])
        hook_template = random.choice(hooks_list)
        hook = hook_template.format(topic=topic, niche=niche.capitalize())

        # Construct title
        title = f"{topic.title()}: The {goal.replace('_', ' ').title()} Strategy"

        # Construct concept
        concept = (
            f"An engaging {format_type.replace('_', ' ').title()} tailored for {audience}. "
            f"Focuses on delivering high value around '{topic}' with a {tone} tone to maximize {goal.replace('_', ' ')}."
        )

        # Objective
        objective = (
            f"Capture attention in the first 3 seconds, establish authority on {topic}, "
            f"and guide the viewer to take action ({goal.replace('_', ' ')})."
        )

        # Visual Direction
        visual_direction = (
            f"{niche_info['visuals']} Framing tailored for 9:16 vertical video or 4:5 carousel slides. "
            f"Color grading styled in a {tone} mood with readable contrast."
        )

        # Call to Action
        if goal == 'saves_shares':
            cta = "Save this cheat sheet so you have it ready for your next session! 📌"
        elif goal == 'engagement':
            cta = f"Have you tried this approach to {topic}? Drop your thoughts in the comments! 👇"
        elif goal == 'promote':
            cta = "Tap the link in my bio to get full access before spots fill up! 🚀"
        else:
            cta = "Follow @yourhandle for daily creator tips and strategies! ✨"

        # Caption
        caption = (
            f"{hook}\n\n"
            f"Let's be real: when it comes to {topic}, so many of us overcomplicate things or focus on the wrong details.\n\n"
            f"Here is the breakdown you actually need to know:\n"
            f"1️⃣ Master the basics first before adding complex tools.\n"
            f"2️⃣ Consistency over perfection: test small variations.\n"
            f"3️⃣ Always audit what your audience actually engages with.\n\n"
            f"{cta}\n\n"
            f"{niche_info['hashtags']}"
        )

        return {
            'title': title,
            'niche': niche,
            'format_type': format_type,
            'content_goal': goal,
            'target_audience': audience,
            'tone': tone,
            'difficulty_level': format_info['difficulty'],
            'estimated_effort': format_info['effort'],
            'main_concept': concept,
            'hook': hook,
            'objective': objective,
            'content_outline': format_info['outline_template'],
            'visual_direction': visual_direction,
            'caption': caption,
            'hashtags': niche_info['hashtags'],
            'call_to_action': cta,
            'filming_editing_tips': niche_info['tips'],
        }
