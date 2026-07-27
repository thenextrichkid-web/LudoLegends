import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.wallet import Wallet, WalletTransaction, TransactionType


class WalletService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_wallet(self, user_id: str) -> Wallet:
        result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            wallet = Wallet(id=str(uuid.uuid4()), user_id=user_id, balance=0)
            self.db.add(wallet)
            await self.db.commit()
            await self.db.refresh(wallet)
        return wallet

    async def get_balance(self, user_id: str) -> Wallet:
        return await self.get_or_create_wallet(user_id)

    async def deposit(self, user_id: str, amount: float, reference_id: str | None = None, description: str | None = None) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id)
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
            description=description or f"Deposited ₹{amount}",
        )
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def withdraw(self, user_id: str, amount: float, description: str | None = None) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id)
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
            description=description or f"Withdrawal ₹{amount}",
        )
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def deduct(self, user_id: str, amount: float, tx_type: TransactionType, reference_id: str | None = None, description: str | None = None) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id)
        if wallet.balance < amount:
            raise ValueError("Insufficient balance")

        balance_before = wallet.balance
        wallet.balance -= amount

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
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def credit(self, user_id: str, amount: float, tx_type: TransactionType, reference_id: str | None = None, description: str | None = None) -> WalletTransaction:
        wallet = await self.get_or_create_wallet(user_id)
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
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def get_transactions(self, user_id: str, page: int = 1, per_page: int = 20) -> tuple[list[WalletTransaction], int]:
        wallet = await self.get_or_create_wallet(user_id)
        offset = (page - 1) * per_page

        result = await self.db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(offset).limit(per_page)
        )
        txs = list(result.scalars().all())

        count_result = await self.db.execute(
            select(WalletTransaction).where(WalletTransaction.wallet_id == wallet.id)
        )
        total = len(count_result.scalars().all())
        return txs, total
