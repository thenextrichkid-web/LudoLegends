"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-07-27
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(15), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True, index=True),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.Text, nullable=True),
        sa.Column('role', sa.Enum('player', 'admin', 'super_admin', name='userrole'), nullable=False, server_default='player'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('fcm_token', sa.Text, nullable=True),
        sa.Column('referral_code', sa.String(20), unique=True, nullable=False, index=True),
        sa.Column('referred_by', sa.String(36), nullable=True),
        sa.Column('vip_level', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_earnings', sa.Float, nullable=False, server_default='0'),
        sa.Column('referral_earnings', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_matches', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_wins', sa.Float, nullable=False, server_default='0'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'wallets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), unique=True, nullable=False),
        sa.Column('balance', sa.Float, nullable=False, server_default='0'),
        sa.Column('frozen', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_deposited', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_withdrawn', sa.Float, nullable=False, server_default='0'),
        sa.Column('total_earned', sa.Float, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'wallet_transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('wallet_id', sa.String(36), sa.ForeignKey('wallets.id'), nullable=False),
        sa.Column('type', sa.Enum('deposit', 'withdrawal', 'tournament_entry', 'tournament_win', 'entry_fee', 'prize', 'refund', 'referral_bonus', 'giveaway', 'cashback', 'adjustment', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('balance_before', sa.Float, nullable=False),
        sa.Column('balance_after', sa.Float, nullable=False),
        sa.Column('reference_id', sa.String(36), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'tournaments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('type', sa.Enum('2_player', '4_player', '8_player', '16_player', '32_player', 'league', 'jackpot', 'scheduled', name='tournamenttype'), nullable=False),
        sa.Column('status', sa.Enum('upcoming', 'registration', 'full', 'in_progress', 'completed', 'cancelled', name='tournamentstatus'), nullable=False, server_default='upcoming'),
        sa.Column('entry_fee', sa.Float, nullable=False),
        sa.Column('prize_pool', sa.Float, nullable=False),
        sa.Column('max_participants', sa.Integer, nullable=False),
        sa.Column('current_participants', sa.Integer, nullable=False, server_default='0'),
        sa.Column('starts_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('registration_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('rules', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'tournament_participants',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tournament_id', sa.String(36), sa.ForeignKey('tournaments.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('entry_fee_paid', sa.Float, nullable=False, server_default='0'),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('status', sa.String(20), nullable=False, server_default='registered'),
    )

    op.create_table(
        'matches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tournament_id', sa.String(36), sa.ForeignKey('tournaments.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_progress', 'submitted', 'verified', 'rejected', 'disputed', 'cancelled', name='matchstatus'), nullable=False, server_default='pending'),
        sa.Column('screenshot_url', sa.Text, nullable=True),
        sa.Column('result_notes', sa.Text, nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('auto_moves_used', sa.Float, nullable=False, server_default='0'),
        sa.Column('auto_move_penalty', sa.Float, nullable=False, server_default='0'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'match_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('match_id', sa.String(36), sa.ForeignKey('matches.id'), unique=True, nullable=False),
        sa.Column('winner_id', sa.String(36), nullable=True),
        sa.Column('score', sa.String(50), nullable=True),
        sa.Column('prize_awarded', sa.Float, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'referrals',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('referrer_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('referred_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('bonus_awarded', sa.Float, nullable=False, server_default='0'),
        sa.Column('milestone_reached', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'rewards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.Enum('referral_bonus', 'cashback', 'weekly_giveaway', 'monthly_giveaway', 'anniversary_giveaway', 'achievement', 'vip', name='rewardtype'), nullable=False),
        sa.Column('amount', sa.Float, nullable=False, server_default='0'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('claimed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'giveaways',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('type', sa.String(50), nullable=False, server_default='weekly'),
        sa.Column('status', sa.Enum('upcoming', 'active', 'completed', 'cancelled', name='giveawaystatus'), nullable=False, server_default='upcoming'),
        sa.Column('prize_amount', sa.Float, nullable=False),
        sa.Column('winners_count', sa.Integer, nullable=False, server_default='2'),
        sa.Column('qualification_threshold', sa.Float, nullable=False, server_default='0'),
        sa.Column('qualification_description', sa.Text, nullable=True),
        sa.Column('winners', sa.Text, nullable=True),
        sa.Column('winner_ids', sa.Text, nullable=True),
        sa.Column('week_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('week_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('drawn_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'leaderboards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('period', sa.String(20), nullable=False, server_default='weekly'),
        sa.Column('wins', sa.Integer, nullable=False, server_default='0'),
        sa.Column('matches_played', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_earnings', sa.Float, nullable=False, server_default='0'),
        sa.Column('win_rate', sa.Float, nullable=False, server_default='0'),
        sa.Column('rank', sa.Integer, nullable=False, server_default='0'),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.Enum('tournament', 'wallet', 'giveaway', 'referral', 'system', 'promotional', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('data', sa.Text, nullable=True),
        sa.Column('is_read', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'withdrawal_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'processed', name='withdrawalstatus'), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('payment_details', sa.Text, nullable=True),
        sa.Column('reviewed_by', sa.String(36), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'deposit_requests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False, index=True),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', name='depositstatus'), nullable=False, server_default='pending'),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('transaction_id', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=True, index=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', sa.String(36), nullable=True),
        sa.Column('old_value', sa.Text, nullable=True),
        sa.Column('new_value', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('value', sa.Text, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('settings')
    op.drop_table('audit_logs')
    op.drop_table('deposit_requests')
    op.drop_table('withdrawal_requests')
    op.drop_table('notifications')
    op.drop_table('leaderboards')
    op.drop_table('giveaways')
    op.drop_table('rewards')
    op.drop_table('referrals')
    op.drop_table('match_results')
    op.drop_table('matches')
    op.drop_table('tournament_participants')
    op.drop_table('tournaments')
    op.drop_table('wallet_transactions')
    op.drop_table('wallets')
    op.drop_table('users')

    op.execute("DROP TYPE IF EXISTS notificationtype")
    op.execute("DROP TYPE IF EXISTS rewardtype")
    op.execute("DROP TYPE IF EXISTS giveawaystatus")
    op.execute("DROP TYPE IF EXISTS tournamentstatus")
    op.execute("DROP TYPE IF EXISTS tournamenttype")
    op.execute("DROP TYPE IF EXISTS matchstatus")
    op.execute("DROP TYPE IF EXISTS transactiontype")
    op.execute("DROP TYPE IF EXISTS withdrawalstatus")
    op.execute("DROP TYPE IF EXISTS depositstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
