import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('creatorspark.pexels')

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
API_TIMEOUT = 5.0  # 5-second timeout as specified in Requirement 9

# High-quality fallback creator aesthetic photographs with full attribution
FALLBACK_CURATED_PHOTOS = [
    {
        "id": 1001,
        "photographer": "Ron Lach",
        "photographer_url": "https://www.pexels.com/@ron-lach/",
        "alt": "Content creator filming video with ring light and smartphone setup",
        "src": {
            "medium": "https://images.pexels.com/photos/8100784/pexels-photo-8100784.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/8100784/pexels-photo-8100784.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/woman-in-front-of-camera-recording-a-video-8100784/",
        "category": "lifestyle",
        "tip": "Position the ring light at eye level and 45 degrees to one side to avoid reflection glare on glasses."
    },
    {
        "id": 1002,
        "photographer": "Cup of Couple",
        "photographer_url": "https://www.pexels.com/@cupofcouple/",
        "alt": "Aesthetic coffee and notebook morning journaling desk",
        "src": {
            "medium": "https://images.pexels.com/photos/6177651/pexels-photo-6177651.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/6177651/pexels-photo-6177651.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/coffee-and-laptop-on-wooden-table-6177651/",
        "category": "lifestyle",
        "tip": "Top-down flat lays look best when lighting comes from a window on the left side with a neutral background."
    },
    {
        "id": 1003,
        "photographer": "Polina Kovaleva",
        "photographer_url": "https://www.pexels.com/@polina-kovaleva/",
        "alt": "Minimalist skincare serum dropper with soft aesthetic bathroom background",
        "src": {
            "medium": "https://images.pexels.com/photos/6543884/pexels-photo-6543884.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/6543884/pexels-photo-6543884.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/dropper-bottle-of-skin-serum-6543884/",
        "category": "skincare",
        "tip": "Use a macro lens or 3x telephoto on your phone to capture clean refraction through clear glass bottles."
    },
    {
        "id": 1004,
        "photographer": "cottonbro studio",
        "photographer_url": "https://www.pexels.com/@cottonbro/",
        "alt": "Modern fashion creator styling outfit in front of full-length mirror",
        "src": {
            "medium": "https://images.pexels.com/photos/4068314/pexels-photo-4068314.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/4068314/pexels-photo-4068314.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/woman-holding-black-camera-4068314/",
        "category": "fashion",
        "tip": "Keep the mirror completely spotless and stand 6 feet back to avoid wide-angle edge distortion."
    },
    {
        "id": 1005,
        "photographer": "Antoni Shkraba",
        "photographer_url": "https://www.pexels.com/@shkrabaanthony/",
        "alt": "Fitness athlete stretching in warm modern gym studio",
        "src": {
            "medium": "https://images.pexels.com/photos/4397839/pexels-photo-4397839.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/4397839/pexels-photo-4397839.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/woman-in-gray-tank-top-and-black-leggings-exercising-4397839/",
        "category": "fitness",
        "tip": "Capture movement at high shutter speeds (1/500s or 60fps) to eliminate motion blur during active workouts."
    },
    {
        "id": 1006,
        "photographer": "Roman Odintsov",
        "photographer_url": "https://www.pexels.com/@roman-odintsov/",
        "alt": "Delicious artisan toast with avocado and poached egg on ceramic plate",
        "src": {
            "medium": "https://images.pexels.com/photos/4551832/pexels-photo-4551832.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/4551832/pexels-photo-4551832.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/appetizing-bruschetta-with-poached-egg-and-avocado-4551832/",
        "category": "food",
        "tip": "Shoot food right after plating while steam is rising and textures look fresh and glistening."
    },
    {
        "id": 1007,
        "photographer": "Aleksandar Pasaric",
        "photographer_url": "https://www.pexels.com/@apasaric/",
        "alt": "Atmospheric city street at sunset with neon reflections",
        "src": {
            "medium": "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/city-street-during-sunset-2506923/",
        "category": "travel",
        "tip": "The blue hour immediately following sunset provides the most cinematic contrast for urban travel reels."
    },
    {
        "id": 1008,
        "photographer": "Mikhail Nilov",
        "photographer_url": "https://www.pexels.com/@mikhail-nilov/",
        "alt": "Modern clean desk setup with mechanical keyboard and soft ambient backlighting",
        "src": {
            "medium": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&w=600",
            "large": "https://images.pexels.com/photos/7988079/pexels-photo-7988079.jpeg?auto=compress&cs=tinysrgb&w=1200",
        },
        "url": "https://www.pexels.com/photo/modern-workplace-with-computer-and-keyboard-7988079/",
        "category": "technology",
        "tip": "Use a desk screenbar light to illuminate your keyboard without washing out the monitor display."
    }
]


class PexelsService:
    """
    Service wrapper for Pexels visual inspiration search.
    Provides strict 5s timeout, caching, response validation, and curated fallback.
    """

    @classmethod
    def search_photos(cls, query: str = "creator aesthetic", per_page: int = 12) -> dict:
        query_clean = query.strip() or "creator aesthetic"
        cache_key = f"pexels_search_{query_clean}_{per_page}".replace(' ', '_').lower()

        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        api_key = settings.PEXELS_API_KEY

        # If no key is configured, return curated fallback with status notice
        if not api_key:
            logger.info("PEXELS_API_KEY is not configured; using curated fallback inspiration collection.")
            result = {
                "source": "curated_fallback",
                "is_fallback": True,
                "message": "Pexels API key not configured. Displaying CreatorSpark curated stock inspiration.",
                "query": query_clean,
                "photos": cls._filter_fallback(query_clean),
                "total_results": len(FALLBACK_CURATED_PHOTOS),
            }
            return result

        # Attempt API request with 5s timeout
        headers = {"Authorization": api_key}
        params = {
            "query": query_clean,
            "per_page": per_page,
            "orientation": "portrait"
        }

        try:
            response = requests.get(
                PEXELS_SEARCH_URL,
                headers=headers,
                params=params,
                timeout=API_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                photos = []
                for p in data.get("photos", []):
                    photos.append({
                        "id": p.get("id"),
                        "photographer": p.get("photographer", "Unknown"),
                        "photographer_url": p.get("photographer_url", "https://www.pexels.com"),
                        "alt": p.get("alt", "Creator Inspiration"),
                        "src": {
                            "medium": p.get("src", {}).get("medium"),
                            "large": p.get("src", {}).get("large"),
                        },
                        "url": p.get("url", "https://www.pexels.com"),
                        "category": query_clean,
                        "tip": "Analyze how lighting and color palette draw the viewer's eye."
                    })

                result = {
                    "source": "pexels_api",
                    "is_fallback": False,
                    "message": f"Successfully retrieved {len(photos)} visual inspiration photos from Pexels.",
                    "query": query_clean,
                    "photos": photos,
                    "total_results": data.get("total_results", len(photos)),
                }

                # Cache successful result for 1 hour
                cache.set(cache_key, result, timeout=3600)
                return result

            else:
                logger.warning(f"Pexels API responded with status {response.status_code}: {response.text}")
                return {
                    "source": "curated_fallback",
                    "is_fallback": True,
                    "message": f"Pexels service responded with status {response.status_code}. Showing curated inspiration.",
                    "query": query_clean,
                    "photos": cls._filter_fallback(query_clean),
                    "total_results": len(FALLBACK_CURATED_PHOTOS),
                }

        except requests.exceptions.Timeout:
            logger.error("Pexels API request timed out after 5.0 seconds.")
            return {
                "source": "curated_fallback",
                "is_fallback": True,
                "message": "Pexels API request timed out (5s limit). Showing curated inspiration.",
                "query": query_clean,
                "photos": cls._filter_fallback(query_clean),
                "total_results": len(FALLBACK_CURATED_PHOTOS),
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Pexels API request failed: {e}")
            return {
                "source": "curated_fallback",
                "is_fallback": True,
                "message": "Could not connect to external media provider. Showing curated inspiration.",
                "query": query_clean,
                "photos": cls._filter_fallback(query_clean),
                "total_results": len(FALLBACK_CURATED_PHOTOS),
            }

    @classmethod
    def _filter_fallback(cls, query: str) -> list:
        q = query.lower()
        matched = [p for p in FALLBACK_CURATED_PHOTOS if q in p["category"] or q in p["alt"].lower()]
        return matched if matched else FALLBACK_CURATED_PHOTOS
