"""
Proactive Suggestion Engine for PACI Agent.

Analyzes conversation context and tool results to generate helpful,
proactive follow-up suggestions that enhance the user experience.
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from app.context.conversation import ConversationContext


@dataclass
class Suggestion:
    """A proactive suggestion to offer the user."""
    text_ar: str  # Arabic version
    text_en: str  # English version
    trigger_reason: str  # Why this suggestion was generated
    priority: int = 1  # Higher = more important (1-5)
    service_related: Optional[str] = None  # Related PACI service if any


# Suggestion templates based on context patterns
SUGGESTION_TRIGGERS: Dict[str, List[Suggestion]] = {
    # After discussing digital signatures
    "digital_signature": [
        Suggestion(
            text_ar="هل تبي أساعدك تحجز موعد للتوقيع الرقمي؟ 📅",
            text_en="Would you like me to help you book an appointment for digital signature registration? 📅",
            trigger_reason="User discussed digital signatures",
            priority=4,
            service_related="digital_signature"
        ),
        Suggestion(
            text_ar="تبي أشرح لك خطوات التسجيل بالتفصيل؟",
            text_en="Would you like me to walk you through the registration steps?",
            trigger_reason="User asked about digital signatures",
            priority=3,
            service_related="digital_signature"
        ),
    ],

    # After discussing Civil ID
    "civil_id": [
        Suggestion(
            text_ar="تبي أشيك لك على حالة طلبك؟ 🔍",
            text_en="Would you like me to check your application status? 🔍",
            trigger_reason="User discussed Civil ID",
            priority=5,
            service_related="civil_id_status"
        ),
        Suggestion(
            text_ar="أقدر أساعدك تعرف المستندات المطلوبة",
            text_en="I can help you find out the required documents",
            trigger_reason="User mentioned Civil ID",
            priority=3,
            service_related="civil_id_requirements"
        ),
    ],

    # After discussing appointments
    "appointment": [
        Suggestion(
            text_ar="تبي أعرض لك المواعيد المتاحة؟ 📆",
            text_en="Would you like me to show you available appointment slots? 📆",
            trigger_reason="User mentioned appointments",
            priority=5,
            service_related="appointment_booking"
        ),
    ],

    # After discussing renewal
    "renewal": [
        Suggestion(
            text_ar="أقدر أشيك لك إذا بطاقتك قربت تنتهي",
            text_en="I can check if your ID is approaching expiration",
            trigger_reason="User discussed renewal",
            priority=4,
            service_related="civil_id_renewal"
        ),
    ],

    # General PACI inquiry
    "general_paci": [
        Suggestion(
            text_ar="تبي أعرض لك الخدمات الإلكترونية المتاحة؟ 💻",
            text_en="Would you like me to show you the available e-services? 💻",
            trigger_reason="General PACI inquiry",
            priority=2,
            service_related="e_services"
        ),
    ],
}

# Keywords that trigger specific suggestion categories
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "digital_signature": [
        "signature", "sign", "digital", "توقيع", "رقمي", "certificate", "شهادة",
        "encrypt", "تشفير", "pin", "رقم سري"
    ],
    "civil_id": [
        "civil id", "بطاقة", "مدنية", "هوية", "card", "id card", "بطاقة مدنية",
        "civil number", "رقم مدني"
    ],
    "appointment": [
        "appointment", "موعد", "book", "حجز", "schedule", "جدول", "visit", "زيارة",
        "slot", "available"
    ],
    "renewal": [
        "renew", "تجديد", "expire", "انتهاء", "validity", "صلاحية", "extend", "تمديد"
    ],
    "general_paci": [
        "paci", "هيئة", "service", "خدمة", "help", "مساعدة", "information", "معلومات"
    ],
}


class ProactiveSuggestionEngine:
    """
    Analyzes conversation context and generates proactive suggestions.

    This engine makes the agent feel more helpful and anticipatory by:
    - Detecting implicit needs from conversation topics
    - Suggesting relevant next steps after tool executions
    - Offering related services based on discussion context
    """

    def __init__(self):
        self.suggestion_triggers = SUGGESTION_TRIGGERS
        self.topic_keywords = TOPIC_KEYWORDS

    def detect_topics(self, text: str) -> List[str]:
        """
        Detect discussion topics from text using keyword matching.

        Args:
            text: User message or conversation text

        Returns:
            List of detected topic categories
        """
        text_lower = text.lower()
        detected = []

        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(topic)

        return detected

    def get_suggestions_for_topics(
        self,
        topics: List[str],
        language: str = "arabic_kuwaiti",
        max_suggestions: int = 2
    ) -> List[str]:
        """
        Get suggestion texts for the detected topics.

        Args:
            topics: List of detected topic categories
            language: User's language preference
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggestion text strings
        """
        all_suggestions: List[Tuple[int, str]] = []  # (priority, text)

        for topic in topics:
            if topic in self.suggestion_triggers:
                for suggestion in self.suggestion_triggers[topic]:
                    text = suggestion.text_ar if language == "arabic_kuwaiti" else suggestion.text_en
                    all_suggestions.append((suggestion.priority, text))

        # Sort by priority (descending) and take top N
        all_suggestions.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in all_suggestions[:max_suggestions]]

    def analyze_tool_result_for_suggestions(
        self,
        tool_name: str,
        tool_result: str,
        language: str = "arabic_kuwaiti"
    ) -> List[str]:
        """
        Generate suggestions based on tool execution results.

        After a tool runs, this method analyzes the result and suggests
        logical next steps to the user.

        Args:
            tool_name: Name of the executed tool
            tool_result: Result returned by the tool
            language: User's language preference

        Returns:
            List of contextual follow-up suggestions
        """
        suggestions = []

        # PACI knowledge search -> suggest related actions
        if tool_name == "search_paci_knowledge":
            if "signature" in tool_result.lower() or "توقيع" in tool_result:
                suggestions.extend(
                    self.get_suggestions_for_topics(["digital_signature"], language, 1)
                )
            if "civil" in tool_result.lower() or "مدنية" in tool_result:
                suggestions.extend(
                    self.get_suggestions_for_topics(["civil_id"], language, 1)
                )

        # Application status check -> suggest next steps
        if tool_name == "check_application_status":
            if "pending" in tool_result.lower() or "قيد المعالجة" in tool_result:
                if language == "arabic_kuwaiti":
                    suggestions.append("تبيني أذكرك لما يتغير حالة طلبك؟ 🔔")
                else:
                    suggestions.append("Would you like me to notify you when your application status changes? 🔔")

        # Appointment availability -> suggest booking
        if tool_name == "get_appointment_slots":
            if language == "arabic_kuwaiti":
                suggestions.append("تبي أحجز لك واحد من هالمواعيد؟ ✅")
            else:
                suggestions.append("Would you like me to book one of these slots for you? ✅")

        return suggestions[:2]  # Max 2 suggestions

    def generate_context_aware_suggestions(
        self,
        context: ConversationContext,
        current_message: str,
        language: str = "arabic_kuwaiti"
    ) -> List[str]:
        """
        Generate suggestions based on full conversation context.

        This is the main entry point that considers:
        - Current message topics
        - Previous conversation history
        - Mentioned services
        - User's apparent goal

        Args:
            context: Full conversation context
            current_message: The current user message
            language: User's language preference

        Returns:
            List of proactive suggestions
        """
        # Detect topics in current message
        current_topics = self.detect_topics(current_message)

        # Also consider previously discussed topics
        all_relevant_topics = list(set(current_topics + context.all_topics_discussed[-3:]))

        # Get base suggestions from topics
        suggestions = self.get_suggestions_for_topics(all_relevant_topics, language, 2)

        # Add goal-based suggestions
        if context.conversation_goal:
            goal_topics = self.detect_topics(context.conversation_goal)
            goal_suggestions = self.get_suggestions_for_topics(goal_topics, language, 1)
            suggestions.extend(goal_suggestions)

        # Deduplicate and limit
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions[:2]

    def get_greeting_suggestion(
        self,
        is_first_interaction: bool,
        language: str = "arabic_kuwaiti"
    ) -> Optional[str]:
        """
        Get a welcoming suggestion for greeting context.

        Args:
            is_first_interaction: Whether this is the first message
            language: User's language preference

        Returns:
            A welcoming suggestion or None
        """
        if is_first_interaction:
            if language == "arabic_kuwaiti":
                return "كيف أقدر أساعدك اليوم؟ سواء بطاقة مدنية، توقيع رقمي، أو أي خدمة ثانية 😊"
            else:
                return "How can I help you today? Whether it's Civil ID, digital signatures, or any other service 😊"
        return None