"""create billing tables invoices and payments

Revision ID: 001_billing
Revises: 
Create Date: 2026-08-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001_billing'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('tax', sa.Float(), nullable=False),
        sa.Column('service_fee', sa.Float(), nullable=False),
        sa.Column('discount', sa.Float(), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(10), server_default='INR'),
        sa.Column('invoice_status', sa.String(50), server_default='Generated'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_invoices_invoice_number', 'invoices', ['invoice_number'])
    op.create_index('ix_invoices_booking_id', 'invoices', ['booking_id'])
    op.create_index('ix_invoices_user_id', 'invoices', ['user_id'])

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('invoice_id', sa.String(36), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('payment_reference', sa.String(100), nullable=False, unique=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('payment_method', sa.String(50), server_default='DEMO_PAYMENT'),
        sa.Column('payment_status', sa.String(50), server_default='Pending'),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('ix_payments_payment_reference', 'payments', ['payment_reference'])
    op.create_index('ix_payments_invoice_id', 'payments', ['invoice_id'])
    op.create_index('ix_payments_booking_id', 'payments', ['booking_id'])

def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('invoices')
