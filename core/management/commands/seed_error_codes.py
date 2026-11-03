from django.core.management.base import BaseCommand
from core.models import ErrorCode

ERROR_CODES_DATA = [
    {
        "code": "CS-AUTH-001",
        "title": "Authentication Required",
        "description": "The requested action requires you to be logged into a verified CreatorSpark user account.",
        "possible_causes": "Session expired, cookies disabled, or attempting to access private creator tools (dashboard, generator, saved ideas, planner) without logging in.",
        "recommended_solution": "Navigate to the Login page, sign in with your credentials, and ensure browser cookies are enabled for this domain.",
        "category": "Authentication",
        "severity": "Medium",
    },
    {
        "code": "CS-AUTH-002",
        "title": "Access Denied / Unauthorized Resource",
        "description": "You do not have permission to view, edit, or delete the specified resource.",
        "possible_causes": "Attempting to access another user's saved idea, planner schedule, or support ticket, or lacking administrative staff privileges.",
        "recommended_solution": "Verify that you are logged into the correct user account that owns the resource. If you believe this is an error, contact support.",
        "category": "Authorization",
        "severity": "High",
    },
    {
        "code": "CS-FORM-001",
        "title": "Invalid Form Submission",
        "description": "One or more form fields failed server-side validation or contain invalid characters.",
        "possible_causes": "Missing required fields, passwords not matching, invalid date formatting in content planner, or field length exceeded.",
        "recommended_solution": "Review the highlighted validation warnings on the form, correct any invalid values, and re-submit.",
        "category": "Validation",
        "severity": "Low",
    },
    {
        "code": "CS-GEN-001",
        "title": "Content Generation Engine Failure",
        "description": "The generator service encountered an unexpected error while constructing the content outline and caption.",
        "possible_causes": "Unrecognized niche parameters, template parsing issue, or temporary system resource bottleneck.",
        "recommended_solution": "Select a supported niche and format from the dropdowns and click 'Generate Ideas' again. If the issue persists, try resetting your filter criteria.",
        "category": "Generator",
        "severity": "Medium",
    },
    {
        "code": "CS-DATA-001",
        "title": "Saved Idea Not Found",
        "description": "The requested content idea record could not be found in your saved library.",
        "possible_causes": "The idea was previously deleted, the URL contains a mistyped ID, or the idea belongs to another creator account.",
        "recommended_solution": "Return to your 'Saved Ideas' library to verify the item exists, or generate a new idea from the Generator tab.",
        "category": "Data",
        "severity": "Low",
    },
    {
        "code": "CS-PLAN-001",
        "title": "Invalid Planner Schedule Entry",
        "description": "Unable to schedule or update the specified post in the content calendar.",
        "possible_causes": "Invalid date format, past date scheduling conflict, or referencing a non-existent saved idea.",
        "recommended_solution": "Ensure the scheduled date is a valid calendar date in YYYY-MM-DD format and all required post details are filled.",
        "category": "Planner",
        "severity": "Low",
    },
    {
        "code": "CS-API-001",
        "title": "External Media Service Unavailable",
        "description": "Could not connect to the third-party stock photography provider (Pexels API).",
        "possible_causes": "Pexels API service outage, network connection timeout (>5 seconds), rate limit exceeded, or missing/invalid API key.",
        "recommended_solution": "The system automatically falls back to curated local creator visual prompts. Check your internet connection or try again later.",
        "category": "Integrations",
        "severity": "Medium",
    },
    {
        "code": "CS-SERVER-001",
        "title": "Unexpected Server Error",
        "description": "An unexpected condition occurred on the server while processing your request (HTTP 500).",
        "possible_causes": "Database connection drop, unhandled runtime exception, or server deployment in progress.",
        "recommended_solution": "Refresh the page after a few moments. If the problem continues, open the Assistant chat widget to create a support ticket with reference CS-SERVER-001.",
        "category": "System",
        "severity": "Critical",
    },
    {
        "code": "CS-TICK-001",
        "title": "Support Ticket Creation Error",
        "description": "Unable to persist support ticket details to the database.",
        "possible_causes": "Empty subject or description, invalid email format for guest tickets, or database constraint violation.",
        "recommended_solution": "Ensure both subject and description are provided with at least 10 characters and try submitting again.",
        "category": "Support",
        "severity": "Medium",
    },
    {
        "code": "CS-MONGO-001",
        "title": "Conversation Storage Degraded",
        "description": "MongoDB chat persistence is temporarily unreachable.",
        "possible_causes": "MongoDB Atlas connection URI not configured, network firewall issue, or remote cluster sleeping.",
        "recommended_solution": "The Assistant continues responding to FAQs and error codes deterministically, but past chat sessions will not be permanently stored until MongoDB is reconnected.",
        "category": "Storage",
        "severity": "Low",
    },
]

class Command(BaseCommand):
    help = "Seeds standard SQL ErrorCode catalog entries idempotently."

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in ERROR_CODES_DATA:
            err, created = ErrorCode.objects.update_or_create(
                code=item["code"],
                defaults={
                    "title": item["title"],
                    "description": item["description"],
                    "possible_causes": item["possible_causes"],
                    "recommended_solution": item["recommended_solution"],
                    "category": item["category"],
                    "severity": item["severity"],
                    "is_active": True,
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully seeded ErrorCodes: {created_count} created, {updated_count} updated. Total: {ErrorCode.objects.count()}"
            )
        )
