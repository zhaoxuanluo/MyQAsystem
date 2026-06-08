from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.memory import LongTermMemory
from app.core.vector_store import vector_store

router = APIRouter()


@router.get("/memory")
async def list_memories(kb_id: str, db: AsyncSession = Depends(get_db)):
    """获取指定知识库的所有长期记忆"""
    result = await db.execute(
        select(LongTermMemory)
        .where(LongTermMemory.user_id == kb_id)
        .order_by(desc(LongTermMemory.created_at))
    )
    memories = result.scalars().all()

    return {
        "total": len(memories),
        "items": [
            {
                "id": str(m.id),
                "content": m.content,
                "created_at": m.created_at.isoformat()
            }
            for m in memories
        ]
    }


@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, kb_id: str, db: AsyncSession = Depends(get_db)):
    """用户手动删除某条记忆"""
    memory = await db.get(LongTermMemory, memory_id)
    if not memory or memory.user_id != kb_id:
        raise HTTPException(status_code=404, detail="Memory not found")

    await db.delete(memory)
    await db.commit()

    # 物理抹除
    vector_store.delete_memory(user_id=kb_id, memory_id=memory_id)
    return {"status": "ok", "detail": "记忆已被彻底清除"}