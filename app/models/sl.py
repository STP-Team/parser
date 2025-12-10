from pydantic import BaseModel, Field


class QueueItem(BaseModel):
    title: str
    vqList: list[str]


class NtpNck(BaseModel):
    title: str
    unitId: int
    queues: list[QueueItem]


class SlRootModel(BaseModel):
    ntp_nck: NtpNck


class TotalDataItem(BaseModel):
    text: str
    value: float


class DetailHeader(BaseModel):
    title: str
    key: str


class DetailRow(BaseModel):
    half_hour_text: str = Field(alias="HALF_HOUR_TEXT", description="Период")
    total_entered: int = Field(alias="TOTAL_ENTERED", description="Поступившие чаты")
    total_answered: int = Field(alias="TOTAL_ANSWERED", description="Принятые чаты")
    total_abandoned: int = Field(
        alias="TOTAL_ABANDONED", description="Пропущенные чаты"
    )
    total_to_nck_tech: int = Field(
        alias="TOTAL_TO_NCK_TECH", description="Переливы в НЦКТех"
    )
    average_release_time: int | None = Field(
        None, alias="AVERAGE_RELEASE_TIME", description="Среднее время обработки чатов"
    )
    average_answer_time: int | None = Field(
        None, alias="AVERAGE_ANSWER_TIME", description="Среднее время ожидания ответа"
    )
    sl: float | None = Field(None, alias="SL", description="Service level")


class DetailData(BaseModel):
    headers: list[DetailHeader]
    data: list[DetailRow]


class ReportData(BaseModel):
    totalData: list[TotalDataItem]
    detailData: DetailData
