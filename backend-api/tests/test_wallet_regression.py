"""Regression tests for critical wallet flows — double-spend, race conditions, edge cases."""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.wallet_service import WalletService
from app.models.wallet import TransactionType


@pytest.mark.asyncio
class TestWalletRegression:
    async def test_concurrent_deposits_no_double_count(self, db: AsyncSession):
        import asyncio
        svc = WalletService(db)
        user_id = str(uuid.uuid4())

        async def deposit(amount):
            s = WalletService(db)
            await s.deposit(user_id, amount)

        await asyncio.gather(*[deposit(100.0) for _ in range(5)])
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 500.0

    async def test_withdraw_then_deduct_same_funds(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 100.0)
        await svc.withdraw(user_id, 100.0)

        with pytest.raises(ValueError, match="Insufficient balance"):
            await svc.deduct(user_id, 1.0, TransactionType.ENTRY_FEE)

    async def test_multiple_withdrawals_freeze_correctly(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 500.0)
        await svc.withdraw(user_id, 100.0)
        await svc.withdraw(user_id, 200.0)

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 200.0
        assert wallet.frozen == 300.0

    async def test_refund_after_reject_restores_full_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 300.0)
        await svc.withdraw(user_id, 300.0)

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 0.0
        assert wallet.frozen == 300.0

        await svc.refund(user_id, 300.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 300.0
        assert wallet.frozen == 0.0

    async def test_tournament_entry_flow(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 200.0)
        await svc.deduct(user_id, 50.0, TransactionType.ENTRY_FEE, description="Join tournament")
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 150.0

    async def test_prize_credit_after_match(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 100.0)
        await svc.deduct(user_id, 50.0, TransactionType.ENTRY_FEE)
        await svc.credit(user_id, 500.0, TransactionType.PRIZE, description="Match win")

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 550.0
        assert wallet.total_earned == 500.0

    async def test_cannot_withdraw_more_than_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 99.0)
        with pytest.raises(ValueError, match="Insufficient balance"):
            await svc.withdraw(user_id, 100.0)

    async def test_negative_amount_rejected(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 100.0)
        with pytest.raises((ValueError, Exception)):
            await svc.withdraw(user_id, -50.0)

    async def test_zero_amount_deposit(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        tx = await svc.deposit(user_id, 0.0)
        assert tx.amount == 0.0
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 0.0

    async def test_wallet_created_on_first_operation(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        balance = await svc.get_balance(user_id)
        assert balance is not None
        assert balance.balance == 0.0
