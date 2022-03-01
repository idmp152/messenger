from sqlalchemy import Column, Integer, String, ForeignKey

from messenger.core.models import Base


class Message(Base):
    __tablename__ = "message"

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    content: Column = Column(String)
    author_id: Column = Column(Integer, ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"<Message(content={self.content}, author_id={self.author_id})>"
