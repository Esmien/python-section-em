from dataclasses import dataclass
from abc import ABC, abstractmethod
import datetime
from bs4 import BeautifulSoup


# Константы инфраструктуры
DEFAULT_BASE_URL = "https://spimex.com"
TARGET_CSS_CLASS = "accordeon-inner__item-title link xls"
TARGET_URL_MARKER = "/upload/reports/oil_xls/oil_xls_"
TARGET_EXTENSION = ".xls"
DATE_FORMAT = "%Y%m%d"
################################################################################################


# Бизнес-логика
@dataclass(frozen=True)
class ReportPeriod:
    """ Период, за который ищем отчеты """

    start_date: datetime.date
    end_date: datetime.date


    def contains(self, target_date: datetime.date) -> bool:
        """
            Бизнес-правило: входит ли дата в период?

            Args:
                target_date: дата, которую проверяем на вхождение в период

            Returns:
                True, если дата входит в период
            """

        return self.start_date <= target_date <= self.end_date


# Отчет
@dataclass
class SpimexReport:
    url: str
    report_date: datetime.date


# Интерфейс репозитория (контракт взаимодействия)
class IReportRepository(ABC):
    """ Не важно, как реализован репозиторий, главное, чтобы вернул список отчетов в формате DTO """
    @abstractmethod
    def get_reports(self, source_data: str, period: ReportPeriod) -> list[SpimexReport]:
        pass
##################################################################################################


# Инфраструктура

# Реализация интерфейса
class HtmlReportRepository(IReportRepository):
    """ Реализация репозитория через парсинг HTML с помощью BeautifulSoup """

    def get_reports(self, source_data: str, period: ReportPeriod) -> list[SpimexReport]:
        """
            Получение списка отчетов из HTML

            Args:
                source_data: HTML-строка с отчетами
                period: период, за который ищем отчеты в формате DTO

            Returns:
                список отчетов
            """

        results = []

        # Преобразуем ссылки из HTML в список объектов BS из CSS-класса
        soup = BeautifulSoup(source_data, "html.parser")
        links = soup.find_all("a", class_=TARGET_CSS_CLASS)

        # Парсим ссылки по заданным правилам и преобразуем к единому виду
        for link in links:
            href = link.get("href")
            if not href:
                continue

            clean_href = href.split("?")[0]
            if TARGET_URL_MARKER not in clean_href or not clean_href.endswith(TARGET_EXTENSION):
                continue

            # Парсим дату из однородных ссылок
            date_str = clean_href.split(TARGET_URL_MARKER)[-1][:8]
            report_date = datetime.datetime.strptime(date_str, DATE_FORMAT).date()

            # Применяем бизнес-логику и собираем в список валидные DTO
            if period.contains(report_date):
                absolute_url = clean_href if clean_href.startswith("http") else f"{DEFAULT_BASE_URL}{clean_href}"
                results.append(SpimexReport(url=absolute_url, report_date=report_date))

        return results
##################################################################################################


# Сценарий использования
class GetFilteredReportsUseCase:
    """ Сценарий использования: Получить отчеты за нужный период из переданного источника """

    def __init__(self, repository: IReportRepository):
        """ Инициализация сценария использования (абстрактный репозиторий) """
        self.repository = repository

    def execute(self, html_content: str, start: datetime.date, end: datetime.date) -> list[SpimexReport]:
        """
            Выполнение сценария использования

            Args:
                html_content: HTML-строка с отчетами
                start: начальная дата
                end: конечная дата

            Returns:
                список отчетов за период
        """

        # Формируем доменный объект периода
        period = ReportPeriod(start_date=start, end_date=end)

        # Делегируем работу интерфейсу репозитория
        return self.repository.get_reports(html_content, period)