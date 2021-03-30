from wherefore.Message import Message
from datetime import datetime, timezone
from typing import Optional


class DataSource:
    def __init__(self, source_name: str, source_type: str, start_time: datetime):
        self._source_name = source_name
        self._source_type = source_type
        self._processed_messages = 0
        self._start_time = start_time
        self._last_message: Optional[Message] = None
        self._first_offset: Optional[int] = None
        self._first_timestamp: Optional[datetime] = None
        self._repeated_timestamps: int = 0
        self._unordered_timestamps: int = 0

    def process_message(self, msg: Message):
        old_timestamp = None
        if self.last_timestamp is not None:
            old_timestamp = self.last_timestamp
        self._processed_messages += 1
        self._last_message = msg
        if self._first_offset is None:
            self._first_offset = msg.offset
            if msg.timestamp is None:
                self._first_timestamp = msg.kafka_timestamp
            else:
                self._first_timestamp = msg.timestamp
        if old_timestamp is not None:
            if old_timestamp == self.last_timestamp:
                self._repeated_timestamps += 1
            elif old_timestamp > self.last_timestamp:
                self._unordered_timestamps += 1

    def __repr__(self):
        return "DataSource: " + self.__str__()

    def __str__(self):
        return f"{self.source_name} (type: {self.source_type})"

    def __eq__(self, other: "DataSource"):
        return self.source_name == other.source_name and self.source_type == other.source_type

    def __lt__(self, other: "DataSource"):
        return self.source_name.lower() < other.source_name.lower() or self.source_type < other.source_type

    @property
    def source_name(self) -> str:
        return self._source_name

    @property
    def first_offset(self) -> int:
        return self._first_offset

    @property
    def first_timestamp(self) -> datetime:
        return self._first_timestamp

    @property
    def repeated_timestamps(self) -> int:
        return self._repeated_timestamps

    @property
    def unordered_timestamps(self) -> int:
        return self._unordered_timestamps

    @property
    def last_timestamp(self) -> datetime:
        if self._last_message is None:
            return None
        if self._last_message.timestamp is None:
            return self._last_message.kafka_timestamp
        return self._last_message.timestamp

    @property
    def source_type(self) -> str:
        return self._source_type

    @property
    def processed_messages(self) -> int:
        return self._processed_messages

    @property
    def processed_per_second(self) -> float:
        time_diff = datetime.now(tz=timezone.utc) - self._start_time
        return self._processed_messages / time_diff.total_seconds()

    @property
    def messages_per_second(self) -> float:
        try:
            time_diff = self.last_timestamp - self._first_timestamp
            return self._processed_messages / time_diff.total_seconds()
        except ZeroDivisionError:
            return 0.0

    @property
    def last_message(self):
        return self._last_message


