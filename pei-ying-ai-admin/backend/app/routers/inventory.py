from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import InventoryItem, InventoryLog, User
from app.schemas import InventoryItemCreate, InventoryItemResponse
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/items", response_model=InventoryItemResponse)
async def create_item(
    item: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = InventoryItem(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.get("/items", response_model=List[InventoryItemResponse])
async def list_items(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(InventoryItem)
    if category:
        query = query.where(InventoryItem.category == category)
    result = await db.execute(query.order_by(InventoryItem.name))
    return result.scalars().all()

@router.get("/items/low-stock")
async def get_low_stock_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.current_quantity <= InventoryItem.min_quantity)
    )
    items = result.scalars().all()
    return {
        "items": items,
        "total": len(items),
        "suggestions": [
            {"item_id": item.id, "name": item.name, "suggested_quantity": item.min_quantity * 2}
            for item in items
        ]
    }

@router.post("/items/{item_id}/count")
async def update_stock_count(
    item_id: int,
    new_quantity: int,
    note: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    
    log = InventoryLog(
        item_id=item_id,
        change_quantity=new_quantity - item.current_quantity,
        previous_quantity=item.current_quantity,
        new_quantity=new_quantity,
        action_type="adjust",
        note=note,
        recorded_by=current_user.id,
    )
    db.add(log)
    
    item.current_quantity = new_quantity
    item.last_counted_at = datetime.utcnow()
    
    await db.commit()
    return {"message": "库存已更新", "new_quantity": new_quantity}

from datetime import datetime
