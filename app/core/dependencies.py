from dishka import Provider, Scope, make_container
from stp_database.repo.STP import MainRequestsRepo

from app.core.db import get_stp_repo

provider = Provider()


# MainRequestsRepo provider
provider.provide(
    get_stp_repo,
    scope=Scope.REQUEST,
    provides=MainRequestsRepo,
)

container = make_container(provider)
