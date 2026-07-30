from __future__ import annotations

import pytdbot


def get_message_sender_id(
    sender: pytdbot.types.MessageSenderChat | pytdbot.types.MessageSenderUser,
) -> int:
    """Get the ID from :class:`pytdbot.types.MessageSenderUser` or :class:`pytdbot.types.MessageSenderChat`"""

    if isinstance(sender, pytdbot.types.MessageSenderUser):
        return sender.user_id

    return sender.chat_id
