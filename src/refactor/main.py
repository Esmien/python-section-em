import logging
import datetime
from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


# TODO: При появлении новых требований (другие биржи/форматы) вынести настройки в конфигурацию (например, pydantic)
DEFAULT_BASE_URL = "https://spimex.com"
TARGET_CSS_CLASS = "accordeon-inner__item-title link xls"
TARGET_URL_MARKER = "/upload/reports/oil_xls/oil_xls_"
TARGET_EXTENSION = ".xls"
DATE_FORMAT = "%Y%m%d"

# Экономим память и делаем DTO хэшируемыми
@dataclass(slots=True, frozen=True)
class SpimexReport:
    absolute_url: str
    report_date: date

# TODO: Если логика парсинга будет усложняться, разбить эту функцию по SRP:
# 1. Extractor (извлекает сырые ссылки из HTML)
# 2. Parser (превращает ссылку в DTO с датой)
# 3. Filter (фильтрует по датам)
def parse_page_links(
        html: str,
        start_date: date,
        end_date: date,
        base_url: str = DEFAULT_BASE_URL
) -> list[SpimexReport]:
    """
        Парсит ссылки на бюллетени из HTML и фильтрует их по заданному диапазону дат.

        Args:
            html: HTML-страница со ссылками
            start_date: Начальная дата диапазона
            end_date: Конечная дата диапазона
            base_url: Базовый URL для построения абсолютных ссылок

        Returns:
            Список валидных DTO ссылок на бюллетени
    """

    results: set[SpimexReport] = set()

    # Собираем ссылки из HTML в виде списка объектов BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", class_=TARGET_CSS_CLASS)

    # Проходим по каждой ссылке и извлекаем дату из URL
    for link in links:
        href = link.get("href")
        if not href:
            continue

        # Очищаем ссылку от query-параметров
        clean_href = href.split("?")[0]

        # Валидируем ссылку
        if TARGET_URL_MARKER not in clean_href or not clean_href.endswith(TARGET_EXTENSION):
            continue

        try:
            # Извлекаем дату
            # TODO: При изменении формата URL на сервере лучше перейти на парсинг через regex.
            date_str = clean_href.split(TARGET_URL_MARKER)[-1][:8]
            report_date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()

            # Фильтруем по дате
            if start_date <= report_date <= end_date:
                # Безопасная склейка путей вместо жесткого f"https://spimex.com{href}"
                absolute_url = urljoin(base_url, clean_href)
                results.add(SpimexReport(absolute_url=absolute_url, report_date=report_date))
            else:
                logger.debug(f"Ссылка {clean_href} вне диапазона дат ({report_date})")

        except (ValueError, IndexError) as e:
            # Ловим только ожидаемые ошибки, на остальных просто падаем
            logger.warning(f"Не удалось извлечь дату из ссылки {clean_href}. Ошибка: {e}")

    # Возвращаем список уникальных валидных DTO
    return list(results)