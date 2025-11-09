"""Add unique constraints for waitlist and claim

Revision ID: 4d4f672efad2
Revises: 
Create Date: 2025-11-09 16:28:08.518787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d4f672efad2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add unique constraints for waitlist and claim tables."""
    # Waitlist tablosuna unique constraint ekle
    # Bir kullanıcı aynı drop için sadece bir kez waitlist'e katılabilir
    op.create_unique_constraint(
        'uq_waitlist_drop_user',
        'waitlist',
        ['drop_id', 'user_id']
    )
    
    # Claim tablosuna unique constraint ekle
    # Bir kullanıcı aynı drop için sadece bir claim yapabilir
    op.create_unique_constraint(
        'uq_claim_drop_user',
        'claims',
        ['drop_id', 'user_id']
    )


def downgrade() -> None:
    """Downgrade schema - Remove unique constraints."""
    # Unique constraint'leri kaldır
    op.drop_constraint('uq_claim_drop_user', 'claims', type_='unique')
    op.drop_constraint('uq_waitlist_drop_user', 'waitlist', type_='unique')
