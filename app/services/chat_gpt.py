import openai
import logging

logger = logging.getLogger(__name__)


class ChatGPTService:
    def __init__(
            self,
            api_key: str,
            model: str = "gpt-3.5-turbo"
    ):
        """
        Инициализация сервиса ChatGPT.

        :param api_key: Ваш API-ключ для OpenAI.
        :param model: Модель для анализа (по умолчанию gpt-3.5-turbo).
        """
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    async def analyze(self, aggregated_data: dict) -> str:
        """
        Принимает агрегированные данные, формирует запрос и отправляет его в ChatGPT для анализа.

        :param aggregated_data: Словарь с агрегированными данными за нужный период.
        :return: Ответ от ChatGPT с торговыми рекомендациями.
        """
        prompt = self._create_prompt(aggregated_data)
        try:
            # Асинхронный вызов ChatGPT API (метод acreate доступен в новых версиях openai)
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "Ты являешься финансовым аналитиком, специализирующимся на криптовалютном рынке."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            analysis = response.choices[0].message.content.strip()
            logger.info("Успешно получен ответ от ChatGPT")
            return analysis
        except Exception as e:
            logger.error(f"Ошибка при вызове ChatGPT API: {e}")
            return "Ошибка при вызове ChatGPT API"

    def _create_prompt(self, aggregated_data: dict) -> str:
        """
        Формирует текст запроса для ChatGPT из агрегированных данных.

        :param aggregated_data: Словарь с данными.
        :return: Строка запроса для ChatGPT.
        """
        # Преобразуем данные в строку. Здесь можно использовать json.dumps с отступами для лучшей читаемости.
        data_str = str(aggregated_data)
        prompt = (
            f"Данные анализа биржевых данных:\n{data_str}\n\n"
            "Проведи анализ с учетом следующих технических индикаторов: SMA, EMA, RSI, MACD, ATR.\n"
            "Определи свечные паттерны: Hammer, Inverted Hammer, Bullish Engulfing, Three White Soldiers, Piercing Line, "
            "Hanging Man, Bearish Engulfing, Three Black Crows, Dark Cloud Cover, Doji.\n"
            "Оцени вероятность роста и падения цены в процентах и предоставь подробные торговые рекомендации с учетом использования плеча.\n"
            "Предоставь ответ в структурированном виде с указанием ключевых параметров."
        )
        return prompt
