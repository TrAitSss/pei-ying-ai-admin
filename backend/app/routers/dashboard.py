from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Supplier, InventoryItem, Template, GeneratedDocument, User
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    supplier_count = (await db.execute(select(func.count(Supplier.id)))).scalar()
    item_count = (await db.execute(select(func.count(InventoryItem.id)))).scalar()
    low_stock = (await db.execute(
        select(func.count(InventoryItem.id)).where(
            InventoryItem.current_quantity <= InventoryItem.min_quantity
        )
    )).scalar()
    template_count = (await db.execute(
        select(func.count(Template.id)).where(Template.is_active == True)
    )).scalar()
    doc_count = (await db.execute(select(func.count(GeneratedDocument.id)))).scalar()
    
    return {
        "suppliers": {"total": supplier_count},
        "inventory": {"total": item_count, "low_stock": low_stock},
        "templates": {"total": template_count},
        "documents": {"total": doc_count},
    }

@router.get("/recent-documents")
async def get_recent_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(GeneratedDocument).order_by(GeneratedDocument.created_at.desc()).limit(5)
    )
    docs = result.scalars().all()
    return [
        {"id": d.id, "title": d.title, "status": d.status, "created_at": str(d.created_at)}
        for d in docs
    ]

@router.get("/low-stock-alerts")
async def get_low_stock_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.current_quantity <= InventoryItem.min_quantity
        )
    )
    items = result.scalars().all()
    return [
        {
            "id": item.id,
            "name": item.name,
            "current": item.current_quantity,
            "minimum": item.min_quantity,
            "shortage": item.min_quantity - item.current_quantity,
        }
        for item in items
    ]