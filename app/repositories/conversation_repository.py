import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message

class ConversationRepository:#会话数据访问层：封装会话与消息的全部数据库操作
    # 新建会话：生成会话 ID 后写入数据库，返回带数据库默认值的会话对象
    async def create_conversation(
        self,
        db: AsyncSession,
        title: str,
        user_id: Optional[str] = None,
    ) -> Conversation:
        conversation = Conversation(
            id=f"c_{uuid.uuid4().hex[:8]}",
            title=title,
            user_id=user_id,
            status="active",
        )

        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    # 查询会话列表：只查未归档的，按更新时间倒序，传了 user_id 则只查该用户
    async def list_conversations(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        limit: int = 20,
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.status == "active")
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)

        result = await db.execute(stmt)

        return list(result.scalars().all())

    # 按 ID 查询单个会话：不存在或已归档时返回 None
    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> Optional[Conversation]:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.status == "active",
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    # 新增一条消息：记录角色、内容与 token 用量，写入后返回消息对象
    async def add_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> Message:
        message = Message(
            id=f"m_{uuid.uuid4().hex[:8]}",
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    # 查询某会话的消息列表：按创建时间正序（由早到晚），最多取 limit 条
    async def get_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        limit: int = 50,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    # 归档会话：把状态改为 archived，成功返回 True，会话不存在返回 False
    async def archive_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> bool:
        conversation = await self.get_conversation(
            db=db,
            conversation_id=conversation_id,
        )

        if not conversation:
            return False

        conversation.status = "archived"

        await db.commit()

        return True

conversation_repository = ConversationRepository()#全局单例：无状态对象，供服务层直接复用
