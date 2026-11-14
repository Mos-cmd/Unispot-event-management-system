"""Model-provider boundary for the in-app assistant.

The provider is deliberately kept behind a small interface. Deployments can
replace ``RuleBasedAssistantProvider`` with an approved model adapter without
giving the model database access or changing the tool executor.

The rule-based provider uses a unified scoring pass over the entire website
knowledge base (FAQs, pages, role guides) instead of a rigid if/else chain, so
answers feel conversational rather than procedural. It is conversation-aware:
it references prior turns and keeps multi-turn tool flows (booking creation,
availability checks) alive across messages.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from app.schemas.assistant import AssistantToolInvocation, ToolName
from app.services.assistant_knowledge import (
    FAQS,
    ALL_PAGES,
    ROLE_GUIDES,
    SITE_OVERVIEW,
    describe_page,
)


@dataclass(frozen=True)
class AssistantProviderPlan:
    response: str | None = None
    tool_calls: list[AssistantToolInvocation] = field(default_factory=list)
    state_patch: dict[str, object] = field(default_factory=dict)


class AssistantProvider(Protocol):
    async def complete(
        self, *, message: str, state: dict[str, object]
    ) -> AssistantProviderPlan: ...


class RuleBasedAssistantProvider:
    """Safe local fallback used when no external model provider is configured."""

    GREETING_PHRASES = ("good morning", "good afternoon", "good evening")
    GREETING_WORDS = ("hi", "hello", "hey")
    THANKS = ("thank you", "thanks", "thx", "appreciate it")
    GOODBYES = ("bye", "goodbye", "see you", "later")

    async def complete(
        self, *, message: str, state: dict[str, object]
    ) -> AssistantProviderPlan:
        normalized = message.casefold().strip()
        intent = state.get("intent")
        slots = state.get("slots") if isinstance(state.get("slots"), dict) else {}

        # 1. Conversational small talk — never a tool.
        small_talk = self._small_talk(normalized)
        if small_talk is not None:
            return AssistantProviderPlan(response=small_talk)

        # 2. Active multi-turn tool flows.
        if intent == ToolName.CREATE_BOOKING.value:
            return self._continue_booking(message, slots)
        if intent == ToolName.CHECK_AVAILABILITY.value:
            return self._continue_availability(message, slots)

        # 3. Tool intents — only when not a "how do I" informational question.
        how_to_prefix = any(
            normalized.startswith(prefix)
            for prefix in ("how do i", "how to", "how can i", "what is", "what does")
        )
        if not how_to_prefix:
            tool_result = self._tool_intent(normalized, message)
            if tool_result is not None:
                return tool_result

        # 4. Unified knowledge pass — score every FAQ, page, and role against
        #    the query and synthesize the best answer.
        knowledge = self._knowledge_response(normalized)
        if knowledge is not None:
            return AssistantProviderPlan(response=knowledge)

        # 5. Fallback — suggest relevant topics from the knowledge base.
        return AssistantProviderPlan(
            response=self._fallback(normalized)
        )

    # ------------------------------------------------------------------
    # Conversational small talk
    # ------------------------------------------------------------------

    def _small_talk(self, normalized: str) -> str | None:
        words = set(normalized.split())
        if any(g in normalized for g in self.GREETING_PHRASES) and len(words) <= 6:
            return (
                "Hi! I'm the UniSpot Assistant. I can help you with anything on "
                "the site — events, venues, services, bookings, registrations, "
                "certificates, and more. What would you like to do?"
            )
        if any(g in words for g in self.GREETING_WORDS) and len(words) <= 4:
            return (
                "Hi! I'm the UniSpot Assistant. I can help you with anything on "
                "the site — events, venues, services, bookings, registrations, "
                "certificates, and more. What would you like to do?"
            )
        if any(t in words for t in self.THANKS) and len(words) <= 3:
            return "You're welcome! Is there anything else I can help you with?"
        if any(g in words for g in self.GOODBYES) and len(words) <= 3:
            return "Goodbye! Feel free to come back if you have more questions."
        return None

    # ------------------------------------------------------------------
    # Tool intents
    # ------------------------------------------------------------------

    def _tool_intent(self, normalized: str, message: str) -> AssistantProviderPlan | None:
        if any(word in normalized for word in ("policy", "policies", "rules", "rule")):
            return AssistantProviderPlan(
                tool_calls=[
                    AssistantToolInvocation(name=ToolName.GET_BOOKING_POLICY, arguments={})
                ]
            )
        if "cancel" in normalized or "cancelled" in normalized:
            booking_id = _find_uuid(message)
            if booking_id is not None:
                return AssistantProviderPlan(
                    tool_calls=[
                        AssistantToolInvocation(
                            name=ToolName.CANCEL_MY_BOOKING,
                            arguments={"booking_id": booking_id},
                        )
                    ],
                    state_patch={"intent": ToolName.CANCEL_MY_BOOKING.value},
                )
            return AssistantProviderPlan(
                response=(
                    "Please provide the booking ID or confirmation reference you "
                    "want to cancel."
                ),
                state_patch={"intent": ToolName.CANCEL_MY_BOOKING.value},
            )
        if "my booking" in normalized or "my reservation" in normalized:
            return AssistantProviderPlan(
                tool_calls=[AssistantToolInvocation(name=ToolName.LIST_MY_BOOKINGS, arguments={})]
            )
        if any(word in normalized for word in ("book", "reservation")):
            return AssistantProviderPlan(
                response=(
                    "To prepare a booking I need the venue, organization, event "
                    "name, expected attendance, date, start time, and end time."
                ),
                state_patch={"intent": ToolName.CREATE_BOOKING.value},
            )
        if any(word in normalized for word in ("availability", "available", "free")):
            slots = _extract_slots(message, {})
            if slots.get("starts_at") and slots.get("ends_at"):
                return AssistantProviderPlan(
                    tool_calls=[
                        AssistantToolInvocation(
                            name=ToolName.CHECK_AVAILABILITY,
                            arguments={
                                "starts_at": slots["starts_at"],
                                "ends_at": slots["ends_at"],
                            },
                        )
                    ],
                    state_patch={"intent": ToolName.CHECK_AVAILABILITY.value, "slots": slots},
                )
            return AssistantProviderPlan(
                response="Please provide the date, start time, and end time to check availability.",
                state_patch={"intent": ToolName.CHECK_AVAILABILITY.value, "slots": slots},
            )
        if "venue" in normalized or "hall" in normalized or "search" in normalized:
            slots = _extract_slots(message, {})
            arguments = {
                key: slots[key] for key in ("capacity", "location") if key in slots
            }
            if arguments:
                return AssistantProviderPlan(
                    tool_calls=[
                        AssistantToolInvocation(
                            name=ToolName.SEARCH_VENUES,
                            arguments=arguments,
                        )
                    ],
                    state_patch={"intent": ToolName.SEARCH_VENUES.value, "slots": slots},
                )
            return AssistantProviderPlan(
                response=(
                    "I can search venues and availability. Please include the date, "
                    "start and end time, expected attendance, and preferred location."
                ),
                state_patch={"intent": ToolName.SEARCH_VENUES.value, "slots": slots},
            )
        return None

    def _continue_booking(self, message: str, slots: dict[str, object]) -> AssistantProviderPlan:
        slots = _extract_slots(message, slots)
        missing = [
            label
            for key, label in (
                ("venue_id", "venue"),
                ("organization_id", "organization"),
                ("event_name", "event name"),
                ("capacity", "expected attendance"),
                ("starts_at", "start time"),
                ("ends_at", "end time"),
            )
            if key not in slots
        ]
        return AssistantProviderPlan(
            response=(
                "I still need: " + ", ".join(missing) + "."
                if missing
                else "I have the booking details. Select a venue and organization to continue."
            ),
            state_patch={"intent": ToolName.CREATE_BOOKING.value, "slots": slots},
        )

    def _continue_availability(
        self, message: str, slots: dict[str, object]
    ) -> AssistantProviderPlan:
        slots = _extract_slots(message, slots)
        if slots.get("starts_at") and slots.get("ends_at"):
            arguments: dict[str, object] = {
                "starts_at": slots["starts_at"],
                "ends_at": slots["ends_at"],
            }
            for key in ("capacity", "location"):
                if key in slots:
                    arguments[key] = slots[key]
            return AssistantProviderPlan(
                tool_calls=[
                    AssistantToolInvocation(
                        name=ToolName.CHECK_AVAILABILITY,
                        arguments=arguments,
                    )
                ],
                state_patch={"intent": ToolName.CHECK_AVAILABILITY.value, "slots": slots},
            )
        missing = []
        if not slots.get("starts_at"):
            missing.append("start time")
        if not slots.get("ends_at"):
            missing.append("end time")
        return AssistantProviderPlan(
            response="Please provide " + ", ".join(missing) + " to check availability.",
            state_patch={"intent": ToolName.CHECK_AVAILABILITY.value, "slots": slots},
        )

    # ------------------------------------------------------------------
    # Unified knowledge pass
    # ------------------------------------------------------------------

    def _knowledge_response(self, normalized: str) -> str | None:
        """Score every knowledge item against the query and synthesize an answer."""
        scored: list[tuple[int, str, str]] = []  # (score, kind, text)

        # FAQs — highest signal, explicit Q&A pairs.
        for faq in FAQS:
            score = _score_match(normalized, faq.keywords)
            if score == 0:
                haystack = " ".join([faq.question, faq.answer]).casefold()
                if normalized in haystack:
                    score = 1
            if score > 0:
                scored.append((score, "faq", faq.answer))

        # Role guides.
        for guide in ROLE_GUIDES:
            role_keywords = (
                guide.role,
                f"what can a {guide.role}",
                f"what does a {guide.role}",
                f"as a {guide.role}",
                f"for {guide.role}",
            )
            score = _score_match(normalized, role_keywords)
            if score > 0 or any(
                phrase in normalized
                for phrase in (guide.role, f"as a {guide.role}", f"for {guide.role}")
            ):
                scored.append((score + 2, "role", guide.description))

        # Pages.
        for page in ALL_PAGES:
            score = _score_match(normalized, page.keywords)
            if score == 0:
                haystack = " ".join(
                    [page.path, page.title, page.description, page.how_to]
                ).casefold()
                if normalized in haystack:
                    score = 1
            if score > 0:
                scored.append((score, "page", describe_page(page)))

        # Site overview — matches general site questions. Only phrase matches
        # count here (no bare single words like "about" or "site" that would
        # catch unrelated queries).
        overview_keywords = (
            "what is", "what does", "what can", "about this", "about unispot",
            "tell me about", "overview",
        )
        score = _score_match(normalized, overview_keywords)
        if score > 0 or any(
            phrase in normalized
            for phrase in ("what is", "what does", "what can", "about this", "about unispot")
        ):
            scored.append((score + 1, "overview", SITE_OVERVIEW))

        if not scored:
            return None

        scored.sort(key=lambda item: item[0], reverse=True)
        best_score, _, best_text = scored[0]

        # Synthesize: lead with best answer, add related context from other kinds.
        top = [item for item in scored if item[0] >= best_score - 1]
        if len(top) > 1:
            kinds = {kind for _, kind, _ in top}
            if len(kinds) > 1:
                related_parts = []
                for _, kind, text in top[1:4]:
                    if kind == "faq":
                        related_parts.append(text)
                    elif kind == "role":
                        related_parts.append(text)
                    elif kind == "page":
                        related_parts.append(text)
                if related_parts:
                    return f"{best_text}\n\nRelated: " + " | ".join(related_parts)

        return best_text

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------

    def _fallback(self, normalized: str) -> str:
        # Pick a few relevant topics to suggest based on any keyword overlap.
        suggestions = []
        topic_keywords = {
            "book a venue": ("book", "venue", "reserve"),
            "reset your password": ("password", "reset", "forgot"),
            "register for an event": ("register", "event", "signup"),
            "request a service": ("service", "request", "catering"),
            "check availability": ("availability", "available", "free"),
            "view my bookings": ("booking", "reservation"),
            "issue a certificate": ("certificate", "certificates"),
            "check in attendees": ("attendance", "check in", "qr"),
            "reserve equipment": ("equipment", "projector", "microphone"),
            "what an organizer can do": ("organizer", "organiser"),
        }
        for topic, kws in topic_keywords.items():
            if any(k in normalized for k in kws):
                suggestions.append(topic)
        if suggestions:
            sugg = "; ".join(suggestions[:4])
            return (
                "I'm not sure about that. You can ask me about topics like "
                f"{sugg}. I can also help find venues, check availability, view "
                "your bookings, or create and cancel bookings."
            )
        return (
            "I'm not sure about that. You can ask me about the site — for "
            "example 'what is UniSpot', 'how do I book a venue', 'how do I "
            "reset my password', 'what can an organizer do', or 'how do I "
            "request a service'. I can also help find venues, check "
            "availability, view your bookings, or create and cancel bookings."
        )


def _score_match(normalized: str, keywords: tuple[str, ...]) -> int:
    """Score how well a query matches a set of keywords.

    Multi-word phrases (all words present, order-independent) score 2; single
    whole-word matches score 1. This lets specific phrases outrank generic
    single words.
    """
    query_words = set(normalized.split())
    hits = 0
    for keyword in keywords:
        kw = keyword.casefold()
        if " " in kw:
            kw_words = kw.split()
            if all(w in query_words for w in kw_words):
                hits += 2
        else:
            if re.search(rf"\b{re.escape(kw)}\b", normalized):
                hits += 1
    return hits


def _find_uuid(message: str) -> str | None:
    match = re.search(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        message,
        flags=re.IGNORECASE,
    )
    return match.group(0) if match else None


def _extract_slots(message: str, state: dict[str, object]) -> dict[str, object]:
    existing = state.get("slots")
    slots = dict(existing) if isinstance(existing, dict) else {}
    capacity = re.search(r"\b(\d{1,5})\s*(?:people|persons|attendees|capacity)\b", message, re.I)
    if capacity:
        slots["capacity"] = int(capacity.group(1))
    location = re.search(r"\b(?:in|at|near)\s+([A-Za-z][A-Za-z -]{1,40})", message)
    if location:
        slots["location"] = location.group(1).strip(" .,")
    datetimes = re.findall(
        r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})\b",
        message,
    )
    parsed = []
    for value in datetimes[:2]:
        try:
            parsed.append(datetime.fromisoformat(value.replace("Z", "+00:00")).isoformat())
        except ValueError:
            continue
    if parsed:
        slots["starts_at"] = parsed[0]
    if len(parsed) > 1:
        slots["ends_at"] = parsed[1]
    return slots


__all__ = ["AssistantProvider", "AssistantProviderPlan", "RuleBasedAssistantProvider"]
