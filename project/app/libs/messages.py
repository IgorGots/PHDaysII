from pydantic import BaseModel


class TgMessage(BaseModel):
    message_id: int
    chat_id: int
    sender_id: int
    sender_name: str
    sender_message: str
    sender_reaction: str | None = None
