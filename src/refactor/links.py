import datetime
from datetime import date
from dataclasses import dataclass
from bs4 import BeautifulSoup

DEFAULT_BASE_URL = "https://spimex.com"
TARGET_CSS_CLASS = "accordeon-inner__item-title link xls"
TARGET_URL_MARKER = "/upload/reports/oil_xls/oil_xls_"
TARGET_EXTENSION = ".xls"
DATE_FORMAT = "%Y%m%d"


@dataclass
class SpimexReportLink:
    url: str
    date: date


class HtmlExtractor:
    """ Только извлекает сырые ссылки из HTML """

    @staticmethod
    def extract(html: str) -> list[str]:
        """
            Извлекает ссылки из HTML и возвращает их в виде списка.

            Args:
                html: HTML со ссылками

            Returns:
                Список ссылок
        """

        hrefs = []
        # Превращаем HTML в объект BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        # Собираем все ссылки из указанного класса
        links = soup.find_all("a", class_=TARGET_CSS_CLASS)

        # Проходимся по всем ссылкам, отбирая нужные
        for link in links:
            href = link.get("href")
            if not href:
                continue

            clean_href = href.split("?")[0]
            if TARGET_URL_MARKER not in clean_href or not clean_href.endswith(TARGET_EXTENSION):
                continue

            hrefs.append(clean_href)

        return hrefs


class LinkParser:
    """ Превращает сырую строку в DTO """

    @staticmethod
    def parse(href: str) -> SpimexReportLink:
        """
            Парсит ссылку и возвращает DTO

            Args:
                href: Сырая ссылка

            Returns:
                DTO с URL и датой
        """

        # Вытаскиваем дату из URL в нужном формате
        date_str = href.split(TARGET_URL_MARKER)[-1][:8]
        report_date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()

        # Формируем полный URL
        absolute_url = href if href.startswith("http") else f"{DEFAULT_BASE_URL}{href}"

        # Создаем DTO
        return SpimexReportLink(url=absolute_url, date=report_date)


class DateFilter:
    """ Применяет бизнес-правила к списку DTO """

    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date

    def filter_links(self, links: list[SpimexReportLink]) -> list[SpimexReportLink]:
        """
            Фильтрует список DTO по дате и возвращает отфильтрованный список

            Args:
                links: Список DTO

            Returns:
                Отфильтрованный список DTO
        """

        # Фильтруем по дате
        return [link for link in links if self.start_date <= link.date <= self.end_date]



class SpimexReportService:
    """ Оркестратор: склеивает экстрактор, парсер и фильтр в единый процесс """

    def __init__(self, start_date: date, end_date: date):
        # Инициализируем компоненты
        self.extractor = HtmlExtractor()
        self.parser = LinkParser()
        self.date_filter = DateFilter(start_date, end_date)

    def run(self, html: str) -> list[SpimexReportLink]:
        """
            Точка входа в программу

            Args:
                html: HTML со ссылками

            Returns:
                Валидный список DTO
        """

        # Извлекаем сырые ссылки из HTML
        raw_hrefs = self.extractor.extract(html)

        # Преобразуем сырые ссылки в DTO
        parsed_links = [self.parser.parse(href) for href in raw_hrefs]

        # Фильтруем по бизнес-правилам и отдаем наружу
        return self.date_filter.filter_links(parsed_links)


