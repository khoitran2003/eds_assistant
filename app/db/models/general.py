from enum import Enum as EnumType


class Gender(str, EnumType):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DayOfWeek(str, EnumType):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Status(str, EnumType):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    REFUND_REQUESTED = "refund_requested"
    REFUND_APPROVED = "refund_approved"
