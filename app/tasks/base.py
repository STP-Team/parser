import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Type variables for generic classes
T = TypeVar("T")  # Type for data models
ConfigT = TypeVar("ConfigT")  # Type for configuration


@dataclass
class ProcessingConfig(ABC):
    """Базовая конфигурация для обработки данных."""

    update_type: str
    semaphore_limit: int = 10

    @abstractmethod
    def get_delete_func(self) -> Callable[[AsyncSession, ...], Any]:
        """Возвращает функцию удаления старых данных."""
        pass


class APIProcessor(Generic[T, ConfigT], ABC):
    """Базовый класс для обработки API данных."""

    def __init__(self, api: Any):
        self.api = api
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def fetch_data(self, config: ConfigT, **kwargs) -> list[tuple[Any, ...]]:
        """Получает данные из API."""
        pass

    @abstractmethod
    def process_results(
        self, results: list[tuple[Any, ...]], config: ConfigT, **kwargs
    ) -> list[T]:
        """Обрабатывает результаты API и конвертирует в модели данных."""
        pass

    @abstractmethod
    async def save_data(self, data: list[T], config: ConfigT, **kwargs) -> int:
        """Сохраняет данные в БД."""
        pass

    async def process_with_config(self, config: ConfigT, **kwargs) -> int:
        """Универсальная обработка данных с конфигурацией."""
        timer_start = perf_counter()
        self.logger.info(f"Начинаем обработку {config.update_type}")

        try:
            # Получаем данные из API
            results = await self.fetch_data(config, **kwargs)

            # Обрабатываем результаты
            processed_data = self.process_results(results, config, **kwargs)

            if not processed_data:
                self.logger.warning(f"Нет данных для обработки в {config.update_type}")
                return 0

            # Сохраняем в БД
            updated_count = await self.save_data(processed_data, config, **kwargs)

            timer_stop = perf_counter()
            self.logger.info(
                f"Завершена обработка {config.update_type}: "
                f"обработано {updated_count} записей за {timer_stop - timer_start:.2f} секунд"
            )
            return updated_count

        except Exception as e:
            timer_stop = perf_counter()
            self.logger.error(
                f"Ошибка обработки {config.update_type} за {timer_stop - timer_start:.2f} секунд: {e}"
            )
            raise


class ConcurrentAPIFetcher:
    """Утилита для параллельных API запросов с ограничением семафора."""

    def __init__(self, semaphore_limit: int = 10):
        self.semaphore_limit = semaphore_limit
        self.logger = logging.getLogger(self.__class__.__name__)

    async def fetch_parallel(
        self, tasks: list[tuple[Any, ...]], task_executor: Callable[..., Any]
    ) -> list[tuple[Any, ...]]:
        """
        Выполняет список задач параллельно с ограничением семафора.

        Args:
            tasks: Список кортежей с параметрами для task_executor
            task_executor: Функция для выполнения задачи

        Returns:
            Список результатов в том же порядке, что и задачи
        """
        semaphore = asyncio.Semaphore(self.semaphore_limit)

        async def limited_task(task_params):
            async with semaphore:
                return await task_executor(*task_params)

        # Создаем корутины для всех задач
        coroutines = [limited_task(task) for task in tasks]

        # Выполняем параллельно
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Обрабатываем исключения
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Ошибка выполнения задачи {i}: {result}")
                processed_results.append((tasks[i], None))
            else:
                processed_results.append((tasks[i], result))

        return processed_results


class BatchDBOperator:
    """Утилита для массовых операций с БД."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.logger = logging.getLogger(self.__class__.__name__)

    async def bulk_update_with_transaction(
        self,
        updates: list[dict[str, Any]],
        update_func: Callable[[dict[str, Any]], Any],
        operation_name: str,
    ) -> int:
        """
        Выполняет массовые обновления в одной транзакции.

        Args:
            updates: Список словарей с данными для обновления
            update_func: Функция для выполнения одного обновления
            operation_name: Название операции для логирования

        Returns:
            Количество успешно обновленных записей
        """
        if not updates:
            self.logger.info(f"[{operation_name}] Нет данных для обновления")
            return 0

        try:
            updated_count = 0

            for update_data in updates:
                await update_func(update_data)
                updated_count += 1

            await self.session.commit()
            self.logger.info(
                f"[{operation_name}] Успешно обновлено {updated_count} записей одной транзакцией"
            )
            return updated_count

        except Exception as e:
            self.logger.error(f"[{operation_name}] Ошибка при массовом обновлении: {e}")
            await self.session.rollback()
            return 0

    async def bulk_insert_with_cleanup(
        self,
        data_list: list[Any],
        delete_func: Callable[[], Any] | None,
        operation_name: str,
    ) -> int:
        """
        Выполняет массовую вставку с предварительной очисткой данных.

        Args:
            data_list: Список объектов для вставки
            delete_func: Функция для удаления старых данных (опционально)
            operation_name: Название операции для логирования

        Returns:
            Количество вставленных записей
        """
        if not data_list:
            self.logger.warning(f"[{operation_name}] Нет данных для вставки")
            return 0

        try:
            # Удаляем старые данные, если функция предоставлена
            if delete_func:
                await delete_func()

            # Вставляем новые данные
            self.session.add_all(data_list)
            await self.session.commit()

            self.logger.info(
                f"[{operation_name}] Успешно вставлено {len(data_list)} записей"
            )
            return len(data_list)

        except Exception as e:
            self.logger.error(f"[{operation_name}] Ошибка при массовой вставке: {e}")
            await self.session.rollback()
            return 0


def log_processing_time(operation_name: str):
    """Декоратор для логирования времени выполнения операций."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            timer_start = perf_counter()
            logger.info(f"Начинаем {operation_name}")

            try:
                result = await func(*args, **kwargs)
                timer_stop = perf_counter()
                logger.info(
                    f"Завершен {operation_name} за {timer_stop - timer_start:.2f} секунд"
                )
                return result
            except Exception as e:
                timer_stop = perf_counter()
                logger.error(
                    f"Ошибка {operation_name} за {timer_stop - timer_start:.2f} секунд: {e}"
                )
                raise

        return wrapper

    return decorator


def create_lookup_index(
    items: list[Any], key_func: Callable[[Any], str]
) -> dict[str, Any]:
    """Создает индекс для быстрого поиска по ключу."""
    return {key_func(item): item for item in items}


def filter_items(items: list[Any], filter_func: Callable[[Any], bool]) -> list[Any]:
    """Фильтрует элементы по предоставленной функции."""
    return [item for item in items if filter_func(item)]
