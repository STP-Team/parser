import asyncio
import logging
from collections import defaultdict
from time import perf_counter

from sqlalchemy import text
from stp_database.models.KPI import SpecDayKPI, SpecMonthKPI, SpecWeekKPI

from app.api.kpi import KpiAPI
from app.core.db import get_stats_session

logger = logging.getLogger(__name__)


def _create_empty_kpi_record(fullname: str) -> dict:
    """Создает шаблон записи показателей.

    Args:
        fullname: ФИО сотрудника

    Returns:
        Словарь созданного шаблона
    """
    return {
        "fullname": fullname,
        "contacts_count": None,
        "aht": None,
        "flr": None,
        "csi": None,
        "pok": None,
        "delay": None,
    }


def _aggregate_kpi_results(tasks: list, results: list) -> dict:
    """Агрегирует полученные результаты отчета показателей.

    Args:
        tasks: Список асинхронных задач
        results: Список результатов

    Returns:
        Словарь обработанных показателей
    """
    kpi_dict = defaultdict(lambda: _create_empty_kpi_record(""))

    for (report_type, _), res in zip(tasks, results, strict=False):
        # Пропускаем получение показателей если нет ответа от api
        if not res or not res.data:
            logger.warning(f"No data returned for report type: {report_type}")
            continue

        for row in res.data:
            # Сохраняем ФИО при первом попадании
            if not kpi_dict[row.fullname]["fullname"]:
                kpi_dict[row.fullname]["fullname"] = row.fullname

            # Сохраняем кол-во контактов
            total_contacts = getattr(row, "total_contacts", None)
            if total_contacts is not None:
                kpi_dict[row.fullname]["contacts_count"] = int(total_contacts)

            # Сохраняем показатели
            value = getattr(row, report_type, None)
            if value is not None and report_type in ("flr", "csi", "pok", "delay"):
                value = float(value)

            kpi_dict[row.fullname][report_type] = value

    return dict(kpi_dict)


async def _bulk_insert_kpi(kpi_dict: dict, model_class, table_name: str) -> None:
    """Очищает таблицы и вставляет строки показателей.

    Args:
        kpi_dict: Словарь показателей
        model_class: Модель БД
        table_name: Название таблицы
    """
    async with get_stats_session() as session:
        # Очищаем таблицу
        await session.execute(text(f"TRUNCATE TABLE {table_name}"))

        # Вставляем записи одной операцией
        records = [
            model_class(**record) for record in kpi_dict.values() if record["fullname"]
        ]
        session.add_all(records)
        await session.commit()

        logger.info(f"Inserted {len(records)} records into {table_name}")


async def _generic_fill_period(
    api: KpiAPI, period_name: str, days: int, model_class, table_name: str
) -> None:
    """Базовая функция для заполнения показателей KPI для любого периода.

    Args:
        api: Экземпляр API
        period_name: Название периода
        days: Отсчет дней с начала периода
        model_class: Модель БД
        table_name: Название таблицы
    """
    timer_start = perf_counter()
    logger.info(f"Starting {period_name} KPI fill")

    # Создаем параллельные задачи для всех подразделений и отчетов
    tasks = []
    for unit in api.unites:
        for report_type in ["aht", "flr", "csi", "pok", "delay"]:
            coro = api.get_period_kpi(
                division=unit, report=report_type.upper(), days=days
            )
            tasks.append((report_type, coro))

    # Выполняем вызовы API одновременно
    results = await asyncio.gather(*(t[1] for t in tasks), return_exceptions=True)

    # Обрабатываем ошибки
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error in task {tasks[i][0]}: {result}")
            results[i] = None

    # Агрегируем результаты
    kpi_dict = _aggregate_kpi_results(tasks, results)

    if not kpi_dict:
        logger.warning(f"No KPI data to insert for {period_name}")
        return

    # Операции с БД: очищаем + вставляем показатели
    await _bulk_insert_kpi(kpi_dict, model_class, table_name)

    timer_stop = perf_counter()
    logger.info(
        f"Finished {period_name} KPI fill, taken {timer_stop - timer_start:.2f} seconds"
    )


async def fill_kpi(api: KpiAPI) -> None:
    """Основная функция для вызова в планировщике.

    Args:
        api: Экземпляр API KPI

    """
    await _fill_day(api)
    await _fill_week(api)
    await _fill_month(api)


async def _fill_day(api: KpiAPI) -> None:
    """Заполняет дневную таблицу KPI.

    Args:
        api: Экземпляр API
    """
    await _generic_fill_period(api, "daily", 1, SpecDayKPI, "KpiDay")


async def _fill_week(api: KpiAPI) -> None:
    """Заполняет недельную таблицу KPI.

    Args:
        api: Экземпляр API
    """
    await _generic_fill_period(api, "weekly", 7, SpecWeekKPI, "KpiWeek")


async def _fill_month(api: KpiAPI) -> None:
    """Заполняет месячную таблицу KPI.

    Args:
        api: Экземпляр API
    """
    await _generic_fill_period(api, "monthly", 31, SpecMonthKPI, "KpiMonth")
