"""Admin audit service — tracks all admin actions for accountability."""

import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.audit_log import AuditLog
from app.core.logging import get_logger

logger = get_logger("audit_service")


class AuditAction:
    ADMIN_LOGIN = "admin_login"
    USER_ROLE_CHANGE = "user_role_change"
    USER_STATUS_TOGGLE = "user_status_toggle"
    MATCH_CREATION = "match_creation"
    MATCH_VERIFY = "match_verify"
    MATCH_REJECT = "match_reject"
    ROOM_ASSIGNMENT = "room_assignment"
    WITHDRAWAL_APPROVE = "withdrawal_approve"
    WITHDRAWAL_REJECT = "withdrawal_reject"
    TOURNAMENT_CREATE = "tournament_create"
    TOURNAMENT_EDIT = "tournament_edit"
    TOURNAMENT_CANCEL = "tournament_cancel"
    TOURNAMENT_JOIN = "tournament_join"
    WALLET_DEPOSIT = "wallet_deposit"
    WALLET_DEBIT = "wallet_debit"
    WALLET_CREDIT = "wallet_credit"
    WALLET_ADJUSTMENT = "wallet_adjustment"
    CONFIG_CHANGE = "config_change"
    FEATURE_FLAG_TOGGLE = "feature_flag_toggle"


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        user_id: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=json.dumps(old_value, default=str) if old_value else None,
            new_value=json.dumps(new_value, default=str) if new_value else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.db.add(entry)
        await self.db.flush()

        logger.info("Audit: action=%s user=%s entity=%s/%s", action, user_id, entity_type, entity_id)
        return entry

    async def get_logs(
        self,
        user_id: str | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[AuditLog], int]:
        query = select(AuditLog)
        count_query = select(func.count(AuditLog.id))

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
            count_query = count_query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)
            count_query = count_query.where(AuditLog.action == action)
        if entity_type:
            query = query.where(AuditLog.entity_type == entity_type)
            count_query = count_query.where(AuditLog.entity_type == entity_type)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * per_page
        result = await self.db.execute(
            query.order_by(AuditLog.created_at.desc()).offset(offset).limit(per_page)
        )
        logs = list(result.scalars().all())
        return logs, total
