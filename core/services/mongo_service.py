import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from django.conf import settings
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger('creatorspark.mongodb')

class MongoService:
    """
    Dedicated MongoDB integration for chat conversations and assistant feedback.
    Handles network failures and missing URIs gracefully without crashing Django.
    """
    _client: Optional[MongoClient] = None

    @classmethod
    def get_client(cls) -> Optional[MongoClient]:
        if not settings.MONGODB_URI:
            return None
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=2500,  # 2.5s quick timeout
                    connectTimeoutMS=2500,
                )
                # Quick ping to verify connectivity
                cls._client.admin.command('ping')
                cls._ensure_indexes()
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"MongoDB connection failed: {e}. Running in graceful offline mode.")
                cls._client = None
            except Exception as e:
                logger.error(f"Unexpected MongoDB error: {e}")
                cls._client = None
        return cls._client

    @classmethod
    def _ensure_indexes(cls):
        try:
            db = cls.get_db()
            if db is not None:
                db.conversations.create_index([("conversation_id", ASCENDING)], unique=True)
                db.conversations.create_index([("user_id", ASCENDING)])
                db.feedback.create_index([("conversation_id", ASCENDING)])
        except Exception as e:
            logger.warning(f"Failed to ensure MongoDB indexes: {e}")

    @classmethod
    def get_db(cls):
        client = cls.get_client()
        if client is not None:
            return client[settings.MONGODB_DATABASE]
        return None

    @classmethod
    def is_available(cls) -> bool:
        """Returns True if MongoDB connection is active and responsive."""
        if not settings.MONGODB_URI:
            return False
        try:
            client = cls.get_client()
            if client is not None:
                client.admin.command('ping')
                return True
        except Exception:
            return False
        return False

    @classmethod
    def save_message(
        cls,
        conversation_id: str,
        role: str,
        content: str,
        user_id: Optional[int] = None,
        related_code: Optional[str] = None
    ) -> bool:
        """
        Appends a message (role: 'user' or 'assistant') to the conversation document.
        Creates the conversation document if it does not yet exist.
        """
        db = cls.get_db()
        if db is None:
            logger.info("MongoDB unavailable; message not persisted to remote collection.")
            return False

        now = datetime.now(timezone.utc)
        message_doc = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": now.isoformat(),
            "related_code": related_code,
        }

        try:
            db.conversations.update_one(
                {"conversation_id": conversation_id},
                {
                    "$setOnInsert": {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "created_at": now.isoformat(),
                    },
                    "$set": {"updated_at": now.isoformat()},
                    "$push": {"messages": message_doc}
                },
                upsert=True
            )
            return True
        except PyMongoError as e:
            logger.error(f"Failed to save message in MongoDB: {e}")
            return False

    @classmethod
    def get_conversation_history(
        cls,
        conversation_id: str,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves message list for a specific conversation.
        If user_id is provided, ensures user isolation.
        """
        db = cls.get_db()
        if db is None:
            return []

        try:
            query: Dict[str, Any] = {"conversation_id": conversation_id}
            if user_id is not None:
                query["user_id"] = user_id

            doc = db.conversations.find_one(query)
            if doc and "messages" in doc:
                return doc["messages"]
            return []
        except PyMongoError as e:
            logger.error(f"Failed to fetch conversation history: {e}")
            return []

    @classmethod
    def save_feedback(
        cls,
        conversation_id: str,
        rating: int,
        feedback_text: str = "",
        user_id: Optional[int] = None
    ) -> bool:
        """
        Saves user rating and feedback text to the feedback collection.
        """
        db = cls.get_db()
        if db is None:
            logger.info("MongoDB unavailable; feedback not saved to remote collection.")
            return False

        now = datetime.now(timezone.utc)
        feedback_doc = {
            "feedback_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "user_id": user_id,
            "rating": rating,
            "feedback_text": feedback_text.strip(),
            "created_at": now.isoformat(),
        }

        try:
            db.feedback.insert_one(feedback_doc)
            return True
        except PyMongoError as e:
            logger.error(f"Failed to save feedback in MongoDB: {e}")
            return False
