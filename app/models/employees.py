from pydantic import BaseModel, Field


class EmployeeUpdateData(BaseModel):
    """Данные для обновления сотрудника."""

    user_id: int
    fullname: str
    birthday: str | None = None
    employee_id: int | None = None
    employment_date: str | None = None
    is_tutor: bool | None = None
    tutor_type: int | None = None


class EmployeeConfig(BaseModel):
    """Конфигурация для обработки данных сотрудников."""

    update_type: str
    semaphore_limit: int = 10
    # filter_func и data_extractor будут переданы как функции отдельно


class Employee(BaseModel):
    id: int = Field(alias="id", description="Идентификатор сотрудника")
    fullname: str = Field(alias="name")
    fired_date: str | None = Field(alias="firedDate")


class EmployeeInfo(BaseModel):
    id: str = Field(alias="EMPLOYEE_ID", description="Идентификатор сотрудника")
    fullname: str = Field(alias="FIO", description="ФИО сотрудника")
    position: str = Field(alias="POST_NAME", description="Должность сотрудника")
    division: str = Field(
        alias="SUBDIVISION_NAME", description="Направление сотрудника"
    )
    unit_id: str = Field(alias="UNIT_ID", description="Идентификатор направления")
    unit_name: str = Field(alias="UNIT_NAME", description="Название направления")
    head_fullname: str | None = Field(
        alias="HEAD_NAME", description="ФИО руководителя сотрудника"
    )
    employment_date: str = Field(
        alias="EMPLOYMENT_DATE", description="День трудоустройства сотрудника"
    )
    transfer_date: str = Field(
        alias="TRANSFER_DATE", description="День изменения должности сотрудника"
    )
    birthday: str | None = Field(
        alias="BIRTHDAY", description="День рождения сотрудника"
    )
    photo: str | None = Field(alias="PHOTO", description="Фотография сотрудника")
    city: str = Field(alias="CITY_NAME", description="Город сотрудника")
    trainee_id: int | None = Field(
        alias="TRAINEE_ID", description="Идентификатор стажера"
    )
    form_id: int | None = Field(alias="FORM_ID")


class PostHistoryItem(BaseModel):
    id: str = Field(alias="ID", description="Идентификатор перевода")
    transfer: str = Field(
        alias="TRANSFER_DATE", description="День изменения должности сотрудника"
    )
    post_name: str = Field(alias="POST_NAME", description="Название новой должности")


class EmployeeData(BaseModel):
    employeeInfo: EmployeeInfo
    postsHistory: list[PostHistoryItem]
