"""Unit tests for WalletService — balance operations, row locking, edge cases."""

import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.wallet_service import WalletService
from app.models.wallet import Wallet, WalletTransaction, TransactionType


@pytest.mark.asyncio
class TestWalletService:
    async def test_get_or_create_creates_new_wallet(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        wallet = await svc.get_or_create_wallet(user_id)
        assert wallet is not None
        assert wallet.user_id == user_id
        assert wallet.balance == 0.0
        assert wallet.frozen == 0.0

    async def test_get_or_create_returns_existing_wallet(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        w1 = await svc.get_or_create_wallet(user_id)
        w2 = await svc.get_or_create_wallet(user_id)
        assert w1.id == w2.id

    async def test_deposit_increases_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        tx = await svc.deposit(user_id, 100.0, description="Test deposit")
        assert tx.amount == 100.0
        assert tx.balance_before == 0.0
        assert tx.balance_after == 100.0
        assert tx.type == TransactionType.DEPOSIT

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 100.0
        assert wallet.total_deposited == 100.0

    async def test_deposit_multiple_times(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 50.0)
        await svc.deposit(user_id, 75.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 125.0
        assert wallet.total_deposited == 125.0

    async def test_withdraw_success(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 200.0)
        tx = await svc.withdraw(user_id, 50.0, description="Test withdrawal")
        assert tx.amount == 50.0
        assert tx.balance_after == 150.0
        assert tx.type == TransactionType.WITHDRAWAL

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 150.0
        assert wallet.frozen == 50.0
        assert wallet.total_withdrawn == 50.0

    async def test_withdraw_insufficient_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 50.0)
        with pytest.raises(ValueError, match="Insufficient balance"):
            await svc.withdraw(user_id, 100.0)

    async def test_withdraw_zero_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        with pytest.raises(ValueError, match="Insufficient balance"):
            await svc.withdraw(user_id, 10.0)

    async def test_deduct_success(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 200.0)
        tx = await svc.deduct(user_id, 30.0, TransactionType.ENTRY_FEE, description="Tournament entry")
        assert tx.amount == 30.0
        assert tx.balance_after == 170.0
        assert tx.type == TransactionType.ENTRY_FEE

    async def test_deduct_insufficient_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 10.0)
        with pytest.raises(ValueError, match="Insufficient balance"):
            await svc.deduct(user_id, 50.0, TransactionType.ENTRY_FEE)

    async def test_credit_increases_balance(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        tx = await svc.credit(user_id, 150.0, TransactionType.PRIZE, description="Prize money")
        assert tx.amount == 150.0
        assert tx.balance_after == 150.0
        wallet = await svc.get_balance(user_id)
        assert wallet.total_earned == 150.0

    async def test_unfreeze(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 200.0)
        await svc.withdraw(user_id, 50.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.frozen == 50.0

        await svc.unfreeze(user_id, 30.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.frozen == 20.0

    async def test_unfreeze_clamps_to_zero(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 100.0)
        await svc.unfreeze(user_id, 999.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.frozen == 0.0

    async def test_refund(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 200.0)
        await svc.withdraw(user_id, 100.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 100.0
        assert wallet.frozen == 100.0

        await svc.refund(user_id, 100.0)
        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 200.0
        assert wallet.frozen == 0.0

    async def test_get_transactions_pagination(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 10.0)
        await svc.deposit(user_id, 20.0)
        await svc.deposit(user_id, 30.0)

        txs, total = await svc.get_transactions(user_id, page=1, per_page=2)
        assert len(txs) == 2
        assert total == 3

        txs2, total2 = await svc.get_transactions(user_id, page=2, per_page=2)
        assert len(txs2) == 1
        assert total2 == 3

    async def test_balance_consistency_after_multiple_operations(self, db: AsyncSession):
        svc = WalletService(db)
        user_id = str(uuid.uuid4())
        await svc.deposit(user_id, 1000.0)
        await svc.deduct(user_id, 100.0, TransactionType.ENTRY_FEE)
        await svc.deduct(user_id, 200.0, TransactionType.ENTRY_FEE)
        await svc.credit(user_id, 500.0, TransactionType.PRIZE)
        await svc.withdraw(user_id, 150.0)

        wallet = await svc.get_balance(user_id)
        assert wallet.balance == 1000.0 - 100.0 - 200.0 + 500.0 - 150.0  # 1050
        assert wallet.total_deposited == 1000.0
        assert wallet.total_withdrawn == 150.0
        assert wallet.total_earned == 500.0
        assert wallet.frozen == 150.0
