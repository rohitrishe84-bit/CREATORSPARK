import re
from typing import Dict, Any, Optional
from core.models import FAQ, ErrorCode, SupportTicket
from core.services.mongo_service import MongoService

class AssistantService:
    """
    Core Assistant logic.
    Primary sources of truth are the SQL ErrorCode and FAQ tables.
    Escalates unknown inquiries to support tickets with user confirmation.
    Logs dialogue to MongoDB when available.
    """

    @classmethod
    def process_message(
        cls,
        message: str,
        conversation_id: str,
        user=None,
        action: Optional[str] = None,
        ticket_subject: Optional[str] = None,
        ticket_desc: Optional[str] = None
    ) -> Dict[str, Any]:
        msg_clean = message.strip()
        user_id = user.id if (user and user.is_authenticated) else None

        # 1. Check if user is confirming ticket creation
        if action == "confirm_ticket":
            subject = (ticket_subject or msg_clean[:60] or "Assistant Escalation").strip()
            description = (ticket_desc or msg_clean or "Issue escalated from chat conversation.").strip()

            ticket = SupportTicket.objects.create(
                user=user if (user and user.is_authenticated) else None,
                guest_name=user.username if (user and user.is_authenticated) else "Guest Creator",
                guest_email=user.email if (user and user.is_authenticated) else "",
                subject=subject,
                description=description,
                priority="Medium",
                status="Open",
            )

            assistant_reply = (
                f"✅ Support ticket **{ticket.ticket_id}** has been created successfully!\n\n"
                f"**Subject:** {ticket.subject}\n"
                f"**Status:** {ticket.status}\n\n"
                f"Our team will review your ticket promptly. You can track this in your Support dashboard."
            )

            # Persist to MongoDB
            MongoService.save_message(conversation_id, "user", f"Confirm ticket: {subject}", user_id=user_id)
            MongoService.save_message(conversation_id, "assistant", assistant_reply, user_id=user_id)

            return {
                "reply": assistant_reply,
                "type": "ticket_created",
                "ticket_id": ticket.ticket_id,
                "can_create_ticket": False,
            }

        # Save user message to MongoDB
        MongoService.save_message(conversation_id, "user", msg_clean, user_id=user_id)

        # 2. Check for Error Code reference in user message (e.g. CS-AUTH-001 or CS-...)
        error_code_match = re.search(r'\bCS-[A-Z]+-\d+\b', msg_clean, re.IGNORECASE)
        if error_code_match:
            code_str = error_code_match.group(0).upper()
            try:
                err = ErrorCode.objects.get(code=code_str, is_active=True)
                reply = (
                    f"### Error Code Explanation: **{err.code}** — {err.title}\n\n"
                    f"**Severity:** {err.severity} | **Category:** {err.category}\n\n"
                    f"**What it means:**\n{err.description}\n\n"
                    f"**Possible Causes:**\n{err.possible_causes}\n\n"
                    f"**Recommended Solution:**\n{err.recommended_solution}"
                )
                MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id, related_code=err.code)
                return {
                    "reply": reply,
                    "type": "error_code",
                    "error_code": err.code,
                    "can_create_ticket": False,
                }
            except ErrorCode.DoesNotExist:
                # If error code format but not in table
                reply = (
                    f"I detected error code **{code_str}**, but it does not match our current database of verified CreatorSpark error codes.\n\n"
                    f"Would you like me to open a support ticket for our engineering team to investigate?"
                )
                MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id)
                return {
                    "reply": reply,
                    "type": "unknown_error_code",
                    "can_create_ticket": True,
                    "suggested_subject": f"Investigation for Error Code {code_str}",
                    "suggested_description": f"Encountered uncatalogued error code {code_str}: {msg_clean}",
                }

        # Also check for common error terms like '404' or '500'
        if '404' in msg_clean:
            err = ErrorCode.objects.filter(code='CS-DATA-001').first()
            if err:
                reply = (
                    f"### 404 Page / Resource Not Found (Ref: {err.code})\n\n"
                    f"{err.description}\n\n"
                    f"**Solution:** {err.recommended_solution}"
                )
                MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id)
                return {"reply": reply, "type": "error_code", "can_create_ticket": False}

        if '500' in msg_clean:
            err = ErrorCode.objects.filter(code='CS-SERVER-001').first()
            if err:
                reply = (
                    f"### 500 Internal Server Error (Ref: {err.code})\n\n"
                    f"{err.description}\n\n"
                    f"**Solution:** {err.recommended_solution}\n\n"
                    f"If this persists, I can file a high-priority ticket for you."
                )
                MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id)
                return {
                    "reply": reply,
                    "type": "error_code",
                    "can_create_ticket": True,
                    "suggested_subject": "500 Server Error Report",
                    "suggested_description": msg_clean
                }

        # 3. Search SQL FAQs for matching question/answer
        words = [w.lower() for w in re.findall(r'\b\w{3,}\b', msg_clean)]
        all_faqs = FAQ.objects.filter(is_active=True)

        best_faq = None
        max_score = 0

        for faq in all_faqs:
            q_text = faq.question.lower()
            a_text = faq.answer.lower()
            score = 0
            for w in words:
                if w in q_text:
                    score += 3
                elif w in a_text:
                    score += 1
            if score > max_score:
                max_score = score
                best_faq = faq

        # If confident FAQ match found (score >= 3)
        if best_faq and max_score >= 3:
            related_faqs = FAQ.objects.filter(category=best_faq.category, is_active=True).exclude(id=best_faq.id)[:2]
            related_text = ""
            if related_faqs:
                related_text = "\n\n**Related Questions:**\n" + "\n".join(f"• {rf.question}" for rf in related_faqs)

            reply = f"**{best_faq.question}**\n\n{best_faq.answer}{related_text}"
            MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id)
            return {
                "reply": reply,
                "type": "faq",
                "faq_id": best_faq.id,
                "can_create_ticket": False,
            }

        # 4. Unknown Question Fallback
        reply = (
            f"I couldn't find a direct answer in the CreatorSpark knowledge base for your inquiry:\n\n"
            f"> \"{msg_clean}\"\n\n"
            f"Would you like me to open a support ticket so our team can help you directly?"
        )
        MongoService.save_message(conversation_id, "assistant", reply, user_id=user_id)
        return {
            "reply": reply,
            "type": "unknown",
            "can_create_ticket": True,
            "suggested_subject": f"Inquiry: {msg_clean[:50]}...",
            "suggested_description": msg_clean,
        }
