import asyncio
import json

import openai
import logging

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

logger = logging.getLogger(__name__)


class ChatGPTService:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        """
        Инициализация сервиса ChatGPT.

        :param api_key: Ваш API-ключ для OpenAI.
        :param model: Модель для анализа (по умолчанию gpt-3.5-turbo).
        :param temperature: Параметр креативности (по умолчанию 0.7).
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze(self, aggregated_data: dict, prompt: str = None) -> dict:
        """
        Отправляет запрос в ChatGPT и возвращает ответ.

        :param aggregated_data: Данные для анализа.
        :param prompt: Текст запроса. Если не передан, он создается автоматически.
        :return: Ответ от ChatGPT в виде строки.
        """
        if prompt is None:
            prompt = self._create_prompt(aggregated_data)

        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system",
                     "content": "Ты являешься финансовым аналитиком, специализирующимся на криптовалютном рынке."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=self.temperature
            )
            analysis = response.choices[0].message.content
            logger.info("Успешно получен ответ от ChatGPT")
            return json.loads(analysis)
        except Exception as e:
            logger.error(f"Ошибка при вызове ChatGPT API: {e}")
            raise ValueError("Ошибка при вызове ChatGPT API")

    def _create_prompt(self, aggregated_data: dict, stage: int = 1, decision_tree: bool = False) -> str:
        """
        Формирует структурированный запрос для ChatGPT.

        :param aggregated_data: Словарь с агрегированными данными.
        :param stage: Этап анализа (1 – первичный, 2 – дополнительный).
        :param decision_tree: Если True, добавить инструкции для построения дерева решений.
        :return: Строка запроса для ChatGPT.
        """
        # Преобразуем данные в отформатированный JSON
        data_str = json.dumps(aggregated_data, default=str, indent=2)

        if stage == 1:
            prompt = (
                "На основе следующих данных проведи первичный анализ:\n\n"
                f"{data_str}\n\n"
                "Выполни следующие задачи:\n"
                "1. Рассчитай технические индикаторы: SMA, EMA, RSI, MACD, ATR.\n"
                "2. Определи свечные паттерны: Hammer, Inverted Hammer, Bullish Engulfing, Three White Soldiers, "
                "Piercing Line, Hanging Man, Bearish Engulfing, Three Black Crows, Dark Cloud Cover, Doji.\n"
                "3. Оцени вероятность роста и падения цены в процентах. Это значение назови 'Index GPT'.\n"
                "4. Дай подробные торговые рекомендации с учетом использования плеча.\n\n"
                "Предоставь ответ в структурированном формате JSON с ключами:\n"
                "  - technical_indicators\n"
                "  - candlestick_patterns\n"
                "  - index_gpt\n"
                "  - recommended_action\n"
                "  - detailed_recommendations"
            )
        elif stage == 2:
            prompt = (
                "Исходя из предыдущего анализа, проведи дополнительное сравнение с архивными данными и реальными изменениями рынка.\n\n"
                f"{data_str}\n\n"
                "Выполни следующие задачи:\n"
                "1. Проведи поиск паттернов и дополнительный анализ для уточнения 'Index GPT'.\n"
                "2. Сравни текущие данные с архивом, оценив изменения динамики.\n"
                "3. На основе этого сформируй итоговый вывод с рекомендацией, включая вероятность изменения цены в процентах.\n"
                "Ответ предоставь в виде JSON с ключами:\n"
                "  - final_index_gpt\n"
                "  - final_recommended_action\n"
                "  - final_detailed_recommendations"
            )
            if decision_tree:
                prompt += (
                    "\nДополнительно, построи дерево решений, подробно описывающее промежуточные шаги анализа и обоснование каждого решения."
                )
        else:
            prompt = f"Данные для анализа:\n{data_str}"
        return prompt

    async def analyze_experimental(self, aggregated_data: dict, stage: int = 1, decision_tree: bool = False) -> dict:
        """
        Проводит анализ с экспериментальными настройками промта.

        :param aggregated_data: Данные для анализа.
        :param stage: Этап анализа (1 - первичный, 2 - дополнительный).
        :param decision_tree: Если True, включить построение дерева решений.
        :return: Распарсенный JSON-ответ от ChatGPT как словарь.
        """
        prompt = self._create_prompt(aggregated_data, stage=stage, decision_tree=decision_tree)
        response: dict = await self.analyze(aggregated_data, prompt=prompt)
        return response

    async def final_analysis(self, primary_analysis: dict, secondary_analysis: dict) -> dict:
        """
        Проводит финальный анализ, объединяя первичный и дополнительный отчеты, и возвращает итоговый вывод.

        :param primary_analysis: Результат первичного анализа.
        :param secondary_analysis: Результат дополнительного анализа.
        :return: Словарь с финальными рекомендациями.
        """
        combined_data = {
            "primary_analysis": primary_analysis,
            "secondary_analysis": secondary_analysis
        }
        prompt = (
            "На основе следующих данных, где 'primary_analysis' содержит первоначальный отчет, а 'secondary_analysis' "
            "содержит дополнительный анализ с учетом архивных данных, проведи итоговый анализ:\n\n"
            f"{json.dumps(combined_data, indent=2, default=str)}\n\n"
            "Пожалуйста, предоставь итоговый вывод в формате JSON с ключами:\n"
            "  - final_index_gpt\n"
            "  - final_recommended_action\n"
            "  - final_detailed_recommendations"
        )
        final_response: dict = await self.analyze(combined_data, prompt=prompt)
        return final_response