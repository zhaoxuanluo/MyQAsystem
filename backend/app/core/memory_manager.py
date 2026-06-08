import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.llm_manager import chat_completion, get_llm_config
from app.models.database import async_session
from app.models.memory import LongTermMemory
from app.core.vector_store import vector_store

# ⚠️ 注意这里：你需要引入你项目中现有的计算向量的函数
# 如果你没有单独封装，你可能需要引入你现有的 bge-m3 实例化代码
# 假设你有一个 get_embedding 异步函数：
from app.core.embedder import get_embedder

logger = logging.getLogger(__name__)


async def extract_and_store_memory_task(user_id: str, user_message: str, ai_response: str, llm_config_id: str | None = None):
    """后台异步任务：提炼并存储长期记忆"""
    try:
        async with async_session() as db:
            llm_config = await get_llm_config(db, llm_config_id)

            if not llm_config:
                logger.error("提取记忆失败: 未找到对应的 LLM 模型配置")
                return

            system_prompt = (
                "你是一个极其敏锐的个人助理记忆中枢。\n"
                "请分析下面的用户与AI的最新对话。只提取关于用户本人的：事实、偏好、身份背景、长期项目状态。\n"
                "要求：\n"
                "1. 必须提炼成一句简短的第三人称陈述句（例如：'用户是一名研究生，正在研究医疗AI'）。\n"
                "2. 忽略寒暄、通用问题、技术报错细节等。\n"
                "3. 如果没有值得长期记忆的信息，请严格只回复'无'这一个字。"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User: {user_message}\nAI: {ai_response}"}
            ]

            memory_text = await chat_completion(messages, llm_config, stream=False)
            memory_text = memory_text.strip()

            if memory_text and memory_text != "无" and "无新记忆" not in memory_text:
                logger.info(f"提炼到新记忆: {memory_text}")

                # 1. 存入 SQLite (获取一个固定 ID)
                new_memory = LongTermMemory(user_id=user_id, content=memory_text)
                db.add(new_memory)
                await db.commit()
                await db.refresh(new_memory)

                # 2. 调用 embedder 把文字变成向量
                embedder = get_embedder()
                vector_dict = embedder.embed_query(memory_text)
                dense_vector = vector_dict["dense"]

                # 3. 存入 Milvus
                vector_store.insert_memory(
                    user_id=user_id,
                    memory_id=new_memory.id,
                    dense_vector=dense_vector,
                    content=memory_text
                )

    except Exception as e:
        logger.error(f"提取记忆失败: {e}")