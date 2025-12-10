from app.api.base import BaseAPI
from app.models.sl import ReportData, SlRootModel


class SlAPI(BaseAPI):
    def __init__(self, session):
        super().__init__(session)
        self.service_url = "genesys/ntp"

    async def get_vq_chat_filter(self) -> SlRootModel | None:
        response = self.post(endpoint=f"{self.service_url}/get-vq-chat-filter")
        try:
            data = SlRootModel.model_validate(response.json())
            return data
        except Exception as e:
            print("Parsing error:", e)
            return None

    async def get_sl(
        self,
        start_date: str,
        stop_date: str,
        units: int | list[int],
        queues: list[str],
    ) -> ReportData | None:
        units_list = units if isinstance(units, list) else [units]

        payload = {
            "startDate": start_date,
            "stopDate": stop_date,
            "units": units_list,
            "queues": queues,
        }

        response = self.post(
            endpoint=f"{self.service_url}/get-chat-sl-report",
            json=payload,
        )

        try:
            data = ReportData.model_validate(response.json())
            return data
        except Exception as e:
            print("Parsing error:", e)
            return None
