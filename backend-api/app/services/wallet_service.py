"""Wallet service with row-level locking for safe balance operations."""

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.core.logging import get_logger

logger = get_logger("wallet_service")


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_wallet(self, user_id: str, for_update: bool = False) -> Wallet:
        """Get or create a wallet. Use for_update=True before balance mutations."""
        query = select(Wallet).where(Wallet.user_id == user_id)
        if for_update:
            query = query.with_for_update()
        result = await self.db.execute(query)
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(id=str(uuid.uuid4()), user_id=user_id, balance=0)
            self.db.add(wallet)
            await self.db.flush()
            await self.db.refresh(wallet)
        return wallet

    async def get_balance(self, user_id: str) -> Wallet:
        """Get wallet balance (read-only, no lock)."""
        return await self.get_or_create_wallet(user_id)

    async def deposit(
        self,
        user_id: str,
        amount: float,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> WalletTransaction:
        """Deposit funds into wallet. Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.total_deposited += amount

        tx = WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet.id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description or f"Deposited {amount}",
        )
        self.db.add(tx)
        await self.db.flush()
        await self.db.refresh(tx)
        return tx

    async def withdraw(
        self,
        user_id: str,
        amount: float,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> WalletTransaction:
        """Withdraw funds (freeze for admin approval). Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        if wallet.balance < amount:
            raise ValueError("Insufficient balance")

        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.frozen += amount
        wallet.total_withdrawn += amount

        tx = WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet.id,
            type=TransactionType.WITHDRAWAL,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description or f"Withdrawal {amount}",
        )
        self.db.add(tx)
        await self.db.flush()
        await self.db.refresh(tx)
        return tx

    async def deduct(
        self,
        user_id: str,
        amount: float,
        tx_type: TransactionType,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> WalletTransaction:
        """Deduct funds (e.g., tournament entry fee). Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        if wallet.balance < amount:
            raise ValueError("Insufficient balance")

        balance_before = wallet.balance
        wallet.balance -= amount
        wallet.frozen += amount

        tx = WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet.id,
            type=tx_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description,
        )
        self.db.add(tx)
        await self.db.flush()
        await self.db.refresh(tx)
        return tx

    async def credit(
        self,
        user_id: str,
        amount: float,
        tx_type: TransactionType,
        reference_id: str | None = None,
        description: str | None = None,
    ) -> WalletTransaction:
        """Credit funds (e.g., prize payout, refund). Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        balance_before = wallet.balance
        wallet.balance += amount
        wallet.total_earned += amount

        tx = WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet.id,
            type=tx_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=wallet.balance,
            reference_id=reference_id,
            description=description,
        )
        self.db.add(tx)
        await self.db.flush()
        await self.db.refresh(tx)
        return tx

    async def unfreeze(self, user_id: str, amount: float) -> None:
        """Unfreeze funds (after withdrawal approval). Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        if amount > wallet.frozen:
            logger.warning("Unfreeze amount %s exceeds frozen %s for user %s", amount, wallet.frozen, user_id)
        wallet.frozen = max(0, wallet.frozen - amount)

    async def refund(self, user_id: str, amount: float) -> None:
        """Return frozen funds to balance (after withdrawal rejection). Acquires row lock."""
        wallet = await self.get_or_create_wallet(user_id, for_update=True)
        actual_refund = min(amount, wallet.frozen)
        if actual_refund < amount:
            logger.warning("Refund amount %s exceeds frozen %s for user %s, refunding %s", amount, wallet.frozen, user_id, actual_refund)
        wallet.frozen = max(0, wallet.frozen - actual_refund)
        wallet.balance += actual_refund

    async def get_transactions(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[WalletTransaction], int]:
        """Get paginated wallet transactions."""
        wallet = await self.get_or_create_wallet(user_id)
        offset = (page - 1) * per_page

        result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        txs = list(result.scalars().all())

        count_result = await self.db.execute(
            select(func.count(WalletTransaction.id))
            .where(WalletTransaction.wallet_id == wallet.id)
        )
        total = count_result.scalar() or 0
        return txs, total
