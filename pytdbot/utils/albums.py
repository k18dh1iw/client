from asyncio import Future

from .. import types


class MediaAlbumFuture(Future):
    def __init__(self, messages: types.Messages):
        super().__init__()
        self.messages = types.Messages(total_count=0, messages=[])
        self.expected_count = messages.total_count

    def set_result(self, result):
        self.messages.messages.append(result)
        self.messages.total_count += 1

        if self.messages.total_count == self.expected_count:
            return super().set_result(self.messages)
