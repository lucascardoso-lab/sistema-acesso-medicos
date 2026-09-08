from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories import dashboard_repository
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def obter_dashboard(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return DashboardResponse(
        cards=dashboard_repository.obter_cards(db),
        serie_30_dias=dashboard_repository.obter_serie_30_dias(db),
        distribuicao_status=dashboard_repository.obter_distribuicao_status(db),
    )
