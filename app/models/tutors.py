from pydantic import BaseModel, Field


class TutorFilter(BaseModel):
    """Фильтр наставника для получения списка всех наставников."""

    id: int = Field(alias="id", description="Идентификатор наставника")
    name: str = Field(alias="name", description="Имя наставника")
    shift_type: int = Field(alias="shiftType", description="Тип смены")
    tutor_type: int = Field(alias="tutorType", description="Тип наставника")
    unit: int = Field(alias="unit", description="Подразделение")


class Unit(BaseModel):
    """Подразделение."""

    id: int = Field(alias="id", description="Идентификатор подразделения")
    name: str = Field(alias="name", description="Название подразделения")
    division: int = Field(alias="division", description="Дивизион")


class ShiftType(BaseModel):
    """Тип смены."""

    id: int = Field(alias="id", description="Идентификатор типа смены")
    name: str = Field(alias="name", description="Название типа смены")


class TutorType(BaseModel):
    """Тип наставника."""

    id: int = Field(alias="id", description="Идентификатор типа наставника")
    name: str = Field(alias="name", description="Название типа наставника")


class GraphFiltersResponse(BaseModel):
    """Ответ API для получения фильтров графика наставников."""

    tutors: list[TutorFilter] = Field(alias="tutors", description="Список наставников")
    units: list[Unit] = Field(alias="units", description="Список подразделений")
    shift_types: list[ShiftType] = Field(
        alias="shiftTypes", description="Список типов смен"
    )
    tutor_types: list[TutorType] = Field(
        alias="tutorTypes", description="Список типов наставников"
    )


class TutorInfo(BaseModel):
    """Информация о наставнике."""

    tutor_id: int = Field(alias="tutorId", description="Идентификатор наставника")
    employee_id: int = Field(alias="employeeId", description="Идентификатор сотрудника")
    name: str = Field(alias="name", description="Имя наставника")
    full_name: str = Field(alias="fullName", description="Полное имя наставника")
    tutor_type: int = Field(alias="tutorType", description="Тип наставника")
    tutor_subtype: int = Field(alias="tutorSubtype", description="Подтип наставника")
    shift_type: int = Field(alias="shiftType", description="Тип смены")
    unit: str = Field(alias="unit", description="Подразделение")


class ShiftPart(BaseModel):
    """Часть смены."""

    day: str = Field(alias="day", description="День смены")
    start: str | None = Field(alias="start", description="Время начала смены")
    end: str | None = Field(alias="end", description="Время окончания смены")
    shift_type: int = Field(alias="shiftType", description="Тип смены")


class Shift(BaseModel):
    """Смена наставника."""

    day: str = Field(alias="day", description="День смены")
    shift_type: int = Field(alias="shiftType", description="Тип смены")
    shift_parts: list[ShiftPart] = Field(alias="shiftParts", description="Части смены")


class Trainee(BaseModel):
    """Стажер под руководством наставника."""

    graph_id: int = Field(alias="graphId", description="Идентификатор графика")
    tutor_id: int = Field(alias="tutorId", description="Идентификатор наставника")
    trainee_id: int = Field(alias="traineeId", description="Идентификатор стажера")
    employee_id: int | None = Field(
        alias="employeeId", default=None, description="Идентификатор сотрудника"
    )
    trainee_type: int = Field(alias="traineeType", description="Тип стажера")
    shift_day: str = Field(alias="shiftDay", description="День смены")
    name: str = Field(alias="name", description="Имя стажера")
    full_name: str = Field(alias="fullName", description="Полное имя стажера")
    shift_start: str | None = Field(
        alias="shiftStart", default=None, description="Время начала смены"
    )
    shift_end: str | None = Field(
        alias="shiftEnd", default=None, description="Время окончания смены"
    )
    is_active: int = Field(alias="isActive", description="Активен ли стажер")


class Tutor(BaseModel):
    """Наставник с информацией о сменах и стажерах."""

    tutor_info: TutorInfo = Field(
        alias="tutorInfo", description="Информация о наставника"
    )
    shifts: list[Shift] = Field(alias="shifts", description="Смены наставника")
    trainees: list[list[Trainee]] = Field(
        alias="trainees", description="Стажеры по дням"
    )


class Day(BaseModel):
    """День в графике."""

    day: str = Field(alias="day", description="Дата")
    weekday: str = Field(alias="weekday", description="День недели")


class TutorGraphResponse(BaseModel):
    """Ответ API для получения графика наставников."""

    tutors: list[Tutor] = Field(alias="tutors", description="Список наставников")
    tutor_map: dict[str, int] = Field(alias="tutorMap", description="Карта наставников")
    days: list[Day] = Field(alias="days", description="Дни в периоде")
    day_map: dict[str, int] = Field(alias="dayMap", description="Карта дней")
