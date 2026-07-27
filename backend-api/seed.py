import asyncio
import uuid
import secrets
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, text
from app.core.database import engine, async_session, Base
from app.models.user import User, UserRole
from app.models.wallet import Wallet, WalletTransaction, TransactionType
from app.models.tournament import Tournament, TournamentParticipant, TournamentType, TournamentStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ADMIN_PHONE = "+910000000000"
PLAYER_PHONE = "+919876543210"


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        existing_admin = await db.execute(select(User).where(User.phone == ADMIN_PHONE))
        if existing_admin.scalar_one_or_none():
            logger.info("Seed data already exists. Skipping.")
            return

        now = datetime.now(timezone.utc)

        admin = User(
            id=str(uuid.uuid4()),
            phone=ADMIN_PHONE,
            email="admin@ludolegends.com",
            name="Demo Admin",
            role="super_admin",
            is_active=True,
            is_verified=True,
            referral_code=f"LL{secrets.token_hex(4).upper()}",
        )
        db.add(admin)

        player = User(
            id=str(uuid.uuid4()),
            phone=PLAYER_PHONE,
            email="player@ludolegends.com",
            name="Demo Player",
            role="player",
            is_active=True,
            is_verified=True,
            referral_code=f"LL{secrets.token_hex(4).upper()}",
        )
        db.add(player)
        await db.flush()

        admin_wallet = Wallet(
            id=str(uuid.uuid4()),
            user_id=admin.id,
            balance=10000.0,
            total_deposited=10000.0,
        )
        db.add(admin_wallet)

        player_wallet = Wallet(
            id=str(uuid.uuid4()),
            user_id=player.id,
            balance=500.0,
            total_deposited=500.0,
        )
        db.add(player_wallet)
        await db.flush()

        db.add(WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=admin_wallet.id,
            type=TransactionType.DEPOSIT,
            amount=10000.0,
            balance_before=0,
            balance_after=10000.0,
            description="Seed: Initial admin deposit",
        ))
        db.add(WalletTransaction(
            id=str(uuid.uuid4()),
            wallet_id=player_wallet.id,
            type=TransactionType.DEPOSIT,
            amount=500.0,
            balance_before=0,
            balance_after=500.0,
            description="Seed: Initial player deposit",
        ))

        tournament = Tournament(
            id=str(uuid.uuid4()),
            name="Sample 4-Player Ludo Championship",
            description="A sample tournament to get you started. Join now and compete for the prize!",
            type=TournamentType.FOUR_PLAYER,
            status=TournamentStatus.UPCOMING,
            entry_fee=50.0,
            prize_pool=200.0,
            max_participants=8,
            current_participants=0,
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=2),
            registration_deadline=now + timedelta(hours=23),
            rules="Standard Ludo rules apply. No auto-move abuse.",
            created_by=admin.id,
        )
        db.add(tournament)

        jackpot = Tournament(
            id=str(uuid.uuid4()),
            name="Jackpot Ludo Night",
            description="High stakes, high rewards. Entry fee is higher but the prize pool is massive.",
            type=TournamentType.JACKPOT,
            status=TournamentStatus.UPCOMING,
            entry_fee=200.0,
            prize_pool=1000.0,
            max_participants=16,
            current_participants=0,
            starts_at=now + timedelta(days=3),
            ends_at=now + timedelta(days=4),
            registration_deadline=now + timedelta(days=2, hours=23),
            rules="Standard Ludo rules. Winner takes all.",
            created_by=admin.id,
        )
        db.add(jackpot)

        await db.commit()
        logger.info("========================================")
        logger.info("  SEED DATA CREATED SUCCESSFULLY")
        logger.info("  Admin:   %s (OTP: 123456 in dev mode)", ADMIN_PHONE)
        logger.info("  Player:  %s (OTP: 123456 in dev mode)", PLAYER_PHONE)
        logger.info("  Admin balance:   ₹10,000")
        logger.info("  Player balance:  ₹500")
        logger.info("  Tournaments: 2 (Sample Championship + Jackpot Night)")
        logger.info("========================================")


if __name__ == "__main__":
    asyncio.run(seed())
