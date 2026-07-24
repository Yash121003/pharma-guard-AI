"""
AIConversation model -- stores chat turns between the user and the AI
Complaint Intake Assistant for a given complaint (the right-hand chat
panel in the reference UI).
"""
import enum

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class AIConversation(Base, TimestampMixin):
    __tablename__ = "ai_conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[int] = mapped_column(ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    # Which AI tool produced this turn, if any (summarize / root_cause / capa / risk / duplicate / completeness / qa)
    tool_used: Mapped[str | None] = mapped_column(Text, nullable=True)

    complaint: Mapped["Complaint"] = relationship(back_populates="conversations")  # noqa: F821

    def __repr__(self) -> str:
        return f"<AIConversation id={self.id} complaint_id={self.complaint_id} role={self.role.value}>"
