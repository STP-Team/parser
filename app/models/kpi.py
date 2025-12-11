from typing import Any

from pydantic import BaseModel, Field, model_validator


class BaseKPIRecord(BaseModel):
    """Базовая модель для общих полей KPI."""

    fact_day: str | None = Field(None, alias="FACT_DAY", description="Дата записи")
    id: int | str | None = Field(
        None, alias="ID", description="Идентификатор сотрудника"
    )
    fullname: str | None = Field(None, alias="FIO", description="ФИО сотрудника")
    subdivision_name: str | None = Field(
        None, alias="SUBDIVISION_NAME", description="Название направления"
    )
    unit_name: str | None = Field(
        None, alias="UNIT_NAME", description="Название подразделения"
    )

    class Config:
        validate_by_name = True


class AHTDataRecord(BaseKPIRecord):
    web_chats: int = Field(0, alias="WEB_CHATS", description="Чаты через Web")
    mob_chats: int = Field(0, alias="MOB_CHATS", description="Чаты через Mobile")
    tgram_chats: int = Field(0, alias="TGRAM_CHATS", description="Чаты через Telegram")
    viber_chats: int = Field(0, alias="VIBER_CHATS", description="Чаты через Viber")
    dhcp_chats: int = Field(0, alias="DHCP_CHATS", description="Чаты через DHCP")
    smartdom_chats: int = Field(
        0, alias="SMARTDOM_CHATS", description="Чаты через SmartDom"
    )
    total_contacts: int = Field(..., description="Общее количество контактов")
    aht: int | None = Field(
        None, alias="AHT", description="Среднее время обработки чата"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_total_contacts(cls, values: dict[str, Any]) -> dict[str, Any]:
        for key in ("TOTAL_CHATS", "TOTAL_CALLS"):
            if key in values:
                values["total_contacts"] = values[key]
                break
        return values


class CSIDataRecord(BaseKPIRecord):
    total_rated_contacts: int = Field(
        ..., description="Общее количество оцененных контактов"
    )
    csi: float | None = Field(
        None, alias="CSI", description="Оценка клиентского сервиса"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_total_contacts(cls, values: dict[str, Any]) -> dict[str, Any]:
        for key in ("TOTAL_RATED_CHATS", "TOTAL_RATED_CALLS"):
            if key in values:
                values["total_rated_contacts"] = values[key]
                break
        return values


class FLRDataRecord(BaseKPIRecord):
    total_contacts: int = Field(..., description="Общее количество контактов")
    total_transfer: int | None = Field(
        None, alias="TOTAL_TRANSFER", description="Общее количество переводов"
    )
    total_service: int = Field(
        ..., alias="TOTAL_SERVICE", description="Общее количество сервисных заявок"
    )
    total_service2: int = Field(
        ..., alias="TOTAL_SERVICE2", description="Общее количество сквозных обращений"
    )
    flr: float | None = Field(None, alias="FLR", description="Значение FLR")

    @model_validator(mode="before")
    @classmethod
    def normalize_total_contacts(cls, values: dict[str, Any]) -> dict[str, Any]:
        for key in ("TOTAL_CHATS", "TOTAL_CALLS"):
            if key in values:
                values["total_contacts"] = values[key]
                break
        return values


class POKDataRecord(BaseKPIRecord):
    total_contacts: int = Field(..., description="Общее количество контактов")
    total_csi: int = Field(..., alias="TOTAL_CSI", description="Кол-во оцененных чатов")
    pok: float | None = Field(..., alias="PERCENT_CSI", description="% оцененных чатов")

    @model_validator(mode="before")
    @classmethod
    def normalize_total_contacts(cls, values: dict[str, Any]) -> dict[str, Any]:
        for key in ("TOTAL_CHATS", "TOTAL_CALLS"):
            if key in values:
                values["total_contacts"] = values[key]
                break
        return values


class DelayDataRecord(BaseKPIRecord):
    # НЦК
    avg_web: float | None = Field(
        None, alias="AVG_WEB", description="Среднее время в Web_chat"
    )
    avg_mobile: float | None = Field(
        None, alias="AVG_MOBILE", description="Среднее время в Mobile_chat"
    )
    avg_dhcp: float | None = Field(
        None, alias="AVG_DHCP", description="Среднее время в DHCP_chat"
    )
    avg_smart: float | None = Field(
        None, alias="AVG_SMART", description="Среднее время в SmartDom_chat"
    )

    # НТП
    work_time: int | None = Field(
        None, alias="WORK_TIME", description="Общее рабочее время"
    )
    unwork_time: int | None = Field(
        None, alias="UNWORK_TIME", description="Время в нерабочем статусе"
    )
    unwork_time_percent: float | None = Field(
        None, alias="UNWORK_TIME_PERCENT", description="% нерабочих статусов"
    )

    delay: float | None = Field(None, description="Общее среднее время")

    @model_validator(mode="before")
    @classmethod
    def normalize_total_contacts(cls, values: dict[str, Any]) -> dict[str, Any]:
        for key in ("AVG_TOTAL", "UNWORK_TIME_PERCENT"):
            if key in values:
                values["delay"] = values[key]
                break
        return values


class SalesDataRecord(BaseKPIRecord):
    """Model for Sales data record."""

    total_sales: int = Field(..., alias="TOTAL_SALES", description="Total sales count")
    sales_amount: float | None = Field(
        None, alias="SALES_AMOUNT", description="Sales amount"
    )
    conversion_rate: float | None = Field(
        None, alias="CONVERSION_RATE", description="Conversion rate"
    )


class GenericKPIDataRecord(BaseKPIRecord):
    additional_fields: dict[str, Any] = Field(
        default_factory=dict, description="Дополнительные динамические поля"
    )

    def __init__(self, **data):
        known_fields = set(self.model_fields.keys())
        base_data = {k: v for k, v in data.items() if k in known_fields}
        additional_data = {k: v for k, v in data.items() if k not in known_fields}
        super().__init__(**base_data, additional_fields=additional_data)


class HeaderDefinition(BaseModel):
    title: str = Field(..., description="Display title for the column")
    key: str = Field(..., description="Field key/identifier")

    class Config:
        validate_by_name = True


KPIDataRecord = (
    AHTDataRecord
    | FLRDataRecord
    | CSIDataRecord
    | POKDataRecord
    | DelayDataRecord
    | GenericKPIDataRecord
)


class KPIResponse(BaseModel):
    data: list[dict[str, Any]] = Field(..., description="Сырые данные KPI")
    headers: list[HeaderDefinition] = Field(..., description="Определение колонок")
    metrics_href: str = Field(..., alias="metricsHref", description="Ссылка на метрики")

    class Config:
        validate_by_name = True


class TypedKPIResponse(BaseModel):
    data: list[KPIDataRecord] = Field(..., description="Типизированные данные KPI")
    headers: list[HeaderDefinition] = Field(..., description="Определение колонок")
    metrics_href: str = Field(..., alias="metricsHref", description="Ссылка на метрики")

    class Config:
        validate_by_name = True
