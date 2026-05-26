from enum import StrEnum


class Channel(StrEnum):
    ZENDESK = "zendesk"
    TELEGRAM = "telegram"
    TEAMS = "teams"
    WHATSAPP = "whatsapp"


class Category(StrEnum):
    HOW_TO = "how_to"
    BILLING = "billing"
    DELIVERY_ISSUE = "delivery_issue"
    AFTER_HOURS = "after_hours"
    COMMERCIAL = "commercial"
    OUTAGE = "outage"
    UNKNOWN = "unknown"
    OTHER = "other"


class Priority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class EscalationTarget(StrEnum):
    FINANCE = "finance"
    SALES = "sales"
    L2_SUPPORT = "l2_support"
    SUPPORT_LEAD = "support_lead"
    GENERAL_SUPPORT = "general_support"


class MessageRole(StrEnum):
    CLIENT = "client"
    AGENT = "agent"
    SYSTEM = "system"
