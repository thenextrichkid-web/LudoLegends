"""Integration tests for withdrawal flow — create, approve, reject, refund."""

import uuid
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.withdrawal import WithdrawalRequest, WithdrawalStatus
from app.services.wallet_service import WalletService
from tests.conftest import auth_header


@pytest.mark.asyncio
class TestWithdrawalIntegration:
    async def test_create_withdrawal(self, client: AsyncClient, db: AsyncSession, test_user: User, user_token: str):
        svc = WalletService(db)
        await svc.deposit(test_user.id, 500.0)

        resp = await client.post(
            "/api/withdrawals/",
            json={"amount": 100.0, "payment_method": "upi", "payment_details": "test@upi"},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["amount"] == 100.0
        assert data["status"] == "pending"

        wallet = await svc.get_balance(test_user.id)
        assert wallet.balance == 400.0
        assert wallet.frozen == 100.0

    async def test_create_withdrawal_insufficient_balance(self, client: AsyncClient, db: AsyncSession, test_user: User, user_token: str):
        svc = WalletService(db)
        await svc.deposit(test_user.id, 50.0)

        resp = await client.post(
            "/api/withdrawals/",
            json={"amount": 100.0, "payment_method": "upi", "payment_details": "test@upi"},
            headers=auth_header(user_token),
        )
        assert resp.status_code == 400

    async def test_create_withdrawal_no_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/withdrawals/",
            json={"amount": 100.0, "payment_method": "upi", "payment_details": "test@upi"},
        )
        assert resp.status_code in (401, 403)

    async def test_approve_withdrawal(self, client: AsyncClient, db: AsyncSession, test_user: User, test_admin: User, admin_token: str):
        svc = WalletService(db)
        await svc.deposit(test_user.id, 500.0)
        tx = await svc.withdraw(test_user.id, 100.0)

        withdrawal = WithdrawalRequest(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            amount=100.0,
            payment_method="upi",
            payment_details="test@upi",
        )
        db.add(withdrawal)
        await db.commit()

        resp = await client.post(
            f"/api/admin/withdrawals/{withdrawal.id}/approve",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

        wallet = await svc.get_balance(test_user.id)
        assert wallet.frozen == 0.0

    async def test_reject_withdrawal_refunds(self, client: AsyncClient, db: AsyncSession, test_user: User, test_admin: User, admin_token: str):
        svc = WalletService(db)
        await svc.deposit(test_user.id, 500.0)
        await svc.withdraw(test_user.id, 100.0)

        withdrawal = WithdrawalRequest(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            amount=100.0,
            payment_method="upi",
            payment_details="test@upi",
        )
        db.add(withdrawal)
        await db.commit()

        resp = await client.post(
            f"/api/admin/withdrawals/{withdrawal.id}/reject",
            params={"reason": "Suspicious activity"},
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 200

        wallet = await svc.get_balance(test_user.id)
        assert wallet.balance == 500.0
        assert wallet.frozen == 0.0

    async def test_cannot_approve_already_processed(self, client: AsyncClient, db: AsyncSession, test_user: User, test_admin: User, admin_token: str):
        svc = WalletService(db)
        await svc.deposit(test_user.id, 500.0)
        await svc.withdraw(test_user.id, 100.0)

        withdrawal = WithdrawalRequest(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            amount=100.0,
            status=WithdrawalStatus.APPROVED,
        )
        db.add(withdrawal)
        await db.commit()

        resp = await client.post(
            f"/api/admin/withdrawals/{withdrawal.id}/approve",
            headers=auth_header(admin_token),
        )
        assert resp.status_code == 400

    async def test_player_cannot_approve(self, client: AsyncClient, db: AsyncSession, test_user: User, user_token: str):
        withdrawal = WithdrawalRequest(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            amount=100.0,
        )
        db.add(withdrawal)
        await db.commit()

        resp = await client.post(
            f"/api/admin/withdrawals/{withdrawal.id}/approve",
            headers=auth_header(user_token),
        )
        assert resp.status_code == 403
