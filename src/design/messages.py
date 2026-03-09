from enum import Enum, auto
from dataclasses import dataclass
from abc import ABC, abstractmethod


class MessageType(Enum):
    TELEGRAM = auto()
    MATTERMOST = auto()
    SLACK = auto()


@dataclass
class JsonMessage:
    message_type: MessageType
    payload: dict


@dataclass
class ParsedMessage:
    """There is no need to describe anything here."""
    text: str = ""
    sender_id: str = None


class BaseMessageParser(ABC):
    @abstractmethod
    def parse(self, message: JsonMessage) -> ParsedMessage:
        pass


class TelegramMessageParser(BaseMessageParser):
    """ Парсер сообщений от Telegram """

    def parse(self, message: JsonMessage) -> ParsedMessage:
        """ Парсит сообщение от Telegram """

        # Тут можно реализовать парсинг сообщения от Telegram
        # ...

        return ParsedMessage(text=message.payload.get("text"))


class MattermostMessageParser(BaseMessageParser):
    """ Парсер сообщений от Mattermost """

    def parse(self, message: JsonMessage) -> ParsedMessage:
        """ Парсит сообщение от Mattermost """

        # Тут можно реализовать парсинг сообщения от Mattermost
        # ...

        return ParsedMessage(text=message.payload.get("text"))


class SlackMessageParser(BaseMessageParser):
    """ Парсер сообщений от Slack """

    def parse(self, message: JsonMessage) -> ParsedMessage:
        """ Парсит сообщение от Slack """

        # Тут можно реализовать парсинг сообщения от Slack
        # ...

        return ParsedMessage(text=message.payload.get("text"))


class MessageParserFactory:
    """ Фабрика для создания парсеров сообщений """

    # Карта парсеров по типам сообщений
    _parsers: dict[MessageType, type[BaseMessageParser]] = {
        MessageType.TELEGRAM: TelegramMessageParser,
        MessageType.MATTERMOST: MattermostMessageParser,
        MessageType.SLACK: SlackMessageParser,
    }


    @classmethod
    def get_parser(cls, message_type: MessageType) -> BaseMessageParser:
        """ Возвращает парсер для указанного типа сообщения """

        # Получаем парсер по типу сообщения
        parser_class = cls._parsers.get(message_type)

        # Если парсер не найден, выбрасываем исключение
        if not parser_class:
            raise ValueError(f"Неизвестный тип сообщения: {message_type}")

        return parser_class()