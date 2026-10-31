"""
Database seed script for Brightloop Subscription Management System (SQLAlchemy 2.0).

Populates initial users, plans, subscriptions, invoices, and payments so
dashboards and analytics render realistic live data out of the box.

Usage:
    python -m backend.seed  OR  python seed.py
"""
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.security import hash_password
from app.models.user import User, Customer, UserRole
from app.models.product import Product
from app.models.plan import SubscriptionPlan
from app.models.subscription import Subscription
from app.models.invoice import Invoice
from app.models.payment import Payment


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_admin = db.query(User).filter(User.email == "admin@brightloop.io").first()
        if existing_admin:
            print("Database already contains seed data. Skipping.")
            return

        print("Seeding Brightloop database with demo records...")
        now = datetime.now(timezone.utc)

        # 1. Users
        admin_id = uuid.uuid4()
        admin = User(
            id=admin_id,
            full_name="Alex Mercer (Admin)",
            email="admin@brightloop.io",
            role=UserRole.ADMIN,
            password_hash=hash_password("Admin@123"),
            is_active=True,
        )

        staff_id = uuid.uuid4()
        staff = User(
            id=staff_id,
            full_name="Sarah Connor (Staff)",
            email="staff@brightloop.io",
            role=UserRole.STAFF,
            password_hash=hash_password("Staff@123"),
            is_active=True,
        )

        cust1_id = uuid.uuid4()
        cust1 = User(
            id=cust1_id,
            full_name="John Doe",
            email="customer@example.com",
            role=UserRole.CUSTOMER,
            password_hash=hash_password("Customer@123"),
            is_active=True,
        )
        cust1_profile = Customer(user_id=cust1_id, company_name="Individual", phone="+919876543210")

        cust2_id = uuid.uuid4()
        cust2 = User(
            id=cust2_id,
            full_name="Acme Corp",
            email="billing@acme.com",
            role=UserRole.CUSTOMER,
            password_hash=hash_password("Acme@123"),
            is_active=True,
        )
        cust2_profile = Customer(user_id=cust2_id, company_name="Acme Corporation", phone="+919876543211")

        cust3_id = uuid.uuid4()
        cust3 = User(
            id=cust3_id,
            full_name="TechStart Labs",
            email="hello@techstart.io",
            role=UserRole.CUSTOMER,
            password_hash=hash_password("Tech@123"),
            is_active=True,
        )
        cust3_profile = Customer(user_id=cust3_id, company_name="TechStart Labs Inc.", phone="+919876543212")

        cust4_id = uuid.uuid4()
        cust4 = User(
            id=cust4_id,
            full_name="Quantum Dynamics",
            email="ops@quantum.ai",
            role=UserRole.CUSTOMER,
            password_hash=hash_password("Quantum@123"),
            is_active=True,
        )
        cust4_profile = Customer(user_id=cust4_id, company_name="Quantum Dynamics LLC", phone="+919876543213")

        db.add_all([admin, staff, cust1, cust1_profile, cust2, cust2_profile, cust3, cust3_profile, cust4, cust4_profile])
        db.flush()

        # 2. Products & Subscription Plans
        prod_core = Product(
            name="Brightloop Core Platform",
            description="Core subscription and billing automation platform",
            category="Software",
            sales_price=Decimal("1499.00"),
            cost_price=Decimal("200.00"),
            currency="INR",
            is_active=True,
        )
        db.add(prod_core)
        db.flush()

        starter = SubscriptionPlan(
            name="Starter Plan",
            description="Ideal for early-stage startups and small projects",
            price=Decimal("1499.00"),
            billing_interval="monthly",
            billing_interval_count=1,
            minimum_quantity=1,
            is_active=True,
            allow_early_cancellation=True,
            allow_pause=True,
        )
        growth = SubscriptionPlan(
            name="Growth Plan",
            description="For growing organizations requiring scaling power",
            price=Decimal("4999.00"),
            billing_interval="monthly",
            billing_interval_count=1,
            minimum_quantity=1,
            is_active=True,
            allow_early_cancellation=True,
            allow_pause=True,
        )
        enterprise = SubscriptionPlan(
            name="Enterprise Annual",
            description="Full-scale enterprise license with priority support",
            price=Decimal("49999.00"),
            billing_interval="annually",
            billing_interval_count=1,
            minimum_quantity=1,
            is_active=True,
            allow_early_cancellation=False,
            allow_pause=False,
        )
        db.add_all([starter, growth, enterprise])
        db.flush()

        # 3. Subscriptions
        sub1 = Subscription(
            subscription_number="SUB-2026-0001",
            customer_id=cust1_id,
            plan_id=growth.id,
            status="ACTIVE",
            billing_frequency="monthly",
            currency="INR",
            subtotal=Decimal("4999.00"),
            tax_amount=Decimal("899.82"),
            total_amount=Decimal("5898.82"),
            start_date=now - timedelta(days=90),
            next_billing_date=now + timedelta(days=30),
        )

        sub2 = Subscription(
            subscription_number="SUB-2026-0002",
            customer_id=cust2_id,
            plan_id=enterprise.id,
            status="ACTIVE",
            billing_frequency="annually",
            currency="INR",
            subtotal=Decimal("49999.00"),
            tax_amount=Decimal("8999.82"),
            total_amount=Decimal("58998.82"),
            start_date=now - timedelta(days=180),
            next_billing_date=now + timedelta(days=185),
        )

        sub3 = Subscription(
            subscription_number="SUB-2026-0003",
            customer_id=cust3_id,
            plan_id=starter.id,
            status="PAUSED",
            billing_frequency="monthly",
            currency="INR",
            subtotal=Decimal("1499.00"),
            tax_amount=Decimal("269.82"),
            total_amount=Decimal("1768.82"),
            start_date=now - timedelta(days=60),
            next_billing_date=now + timedelta(days=15),
            paused_at=now - timedelta(days=10),
        )

        sub4 = Subscription(
            subscription_number="SUB-2026-0004",
            customer_id=cust4_id,
            plan_id=starter.id,
            status="CLOSED",
            billing_frequency="monthly",
            currency="INR",
            subtotal=Decimal("1499.00"),
            tax_amount=Decimal("269.82"),
            total_amount=Decimal("1768.82"),
            start_date=now - timedelta(days=120),
            next_billing_date=now - timedelta(days=20),
            canceled_at=now - timedelta(days=20),
            cancellation_reason="Customer migrated internal platform",
        )
        db.add_all([sub1, sub2, sub3, sub4])
        db.flush()

        # 4. Invoices and Payments (past 3 months)
        # Month -3
        inv_m3 = Invoice(
            invoice_number="INV-2026-0001",
            subscription_id=sub1.id,
            customer_id=cust1_id,
            billing_period_start=now - timedelta(days=90),
            billing_period_end=now - timedelta(days=61),
            issue_date=now - timedelta(days=90),
            due_date=now - timedelta(days=80),
            status="PAID",
            subtotal=Decimal("4999.00"),
            tax_amount=Decimal("899.82"),
            total_amount=Decimal("5898.82"),
            amount_paid=Decimal("5898.82"),
            balance_due=Decimal("0.00"),
        )
        db.add(inv_m3)
        db.flush()
        db.add(Payment(
            payment_number="PAY-2026-0001",
            invoice_id=inv_m3.id,
            amount=Decimal("5898.82"),
            currency="INR",
            payment_method="CREDIT_CARD",
            payment_reference="TXN-PAY-001",
            payment_status="SUCCESS",
            payment_date=now - timedelta(days=89),
        ))

        # Enterprise annual invoice
        inv_ent = Invoice(
            invoice_number="INV-2026-0002",
            subscription_id=sub2.id,
            customer_id=cust2_id,
            billing_period_start=now - timedelta(days=180),
            billing_period_end=now + timedelta(days=185),
            issue_date=now - timedelta(days=180),
            due_date=now - timedelta(days=170),
            status="PAID",
            subtotal=Decimal("49999.00"),
            tax_amount=Decimal("8999.82"),
            total_amount=Decimal("58998.82"),
            amount_paid=Decimal("58998.82"),
            balance_due=Decimal("0.00"),
        )
        db.add(inv_ent)
        db.flush()
        db.add(Payment(
            payment_number="PAY-2026-0002",
            invoice_id=inv_ent.id,
            amount=Decimal("58998.82"),
            currency="INR",
            payment_method="BANK_TRANSFER",
            payment_reference="TXN-WIRE-001",
            payment_status="SUCCESS",
            payment_date=now - timedelta(days=179),
        ))

        # Month -2
        inv_m2_1 = Invoice(
            invoice_number="INV-2026-0003",
            subscription_id=sub1.id,
            customer_id=cust1_id,
            billing_period_start=now - timedelta(days=60),
            billing_period_end=now - timedelta(days=31),
            issue_date=now - timedelta(days=60),
            due_date=now - timedelta(days=50),
            status="PAID",
            subtotal=Decimal("4999.00"),
            tax_amount=Decimal("899.82"),
            total_amount=Decimal("5898.82"),
            amount_paid=Decimal("5898.82"),
            balance_due=Decimal("0.00"),
        )
        inv_m2_2 = Invoice(
            invoice_number="INV-2026-0004",
            subscription_id=sub3.id,
            customer_id=cust3_id,
            billing_period_start=now - timedelta(days=60),
            billing_period_end=now - timedelta(days=31),
            issue_date=now - timedelta(days=60),
            due_date=now - timedelta(days=50),
            status="PAID",
            subtotal=Decimal("1499.00"),
            tax_amount=Decimal("269.82"),
            total_amount=Decimal("1768.82"),
            amount_paid=Decimal("1768.82"),
            balance_due=Decimal("0.00"),
        )
        db.add_all([inv_m2_1, inv_m2_2])
        db.flush()
        db.add_all([
            Payment(payment_number="PAY-2026-0003", invoice_id=inv_m2_1.id, amount=Decimal("5898.82"), currency="INR", payment_method="CREDIT_CARD", payment_reference="TXN-PAY-003", payment_status="SUCCESS", payment_date=now - timedelta(days=59)),
            Payment(payment_number="PAY-2026-0004", invoice_id=inv_m2_2.id, amount=Decimal("1768.82"), currency="INR", payment_method="UPI", payment_reference="TXN-UPI-001", payment_status="SUCCESS", payment_date=now - timedelta(days=58)),
        ])

        # Current Month - Pending / Outstanding invoices
        inv_curr_1 = Invoice(
            invoice_number="INV-2026-0005",
            subscription_id=sub1.id,
            customer_id=cust1_id,
            billing_period_start=now - timedelta(days=2),
            billing_period_end=now + timedelta(days=28),
            issue_date=now - timedelta(days=2),
            due_date=now + timedelta(days=8),
            status="CONFIRMED",
            subtotal=Decimal("4999.00"),
            tax_amount=Decimal("899.82"),
            total_amount=Decimal("5898.82"),
            amount_paid=Decimal("0.00"),
            balance_due=Decimal("5898.82"),
        )
        inv_curr_2 = Invoice(
            invoice_number="INV-2026-0006",
            subscription_id=sub3.id,
            customer_id=cust3_id,
            billing_period_start=now,
            billing_period_end=now + timedelta(days=30),
            issue_date=now,
            due_date=now + timedelta(days=10),
            status="DRAFT",
            subtotal=Decimal("1499.00"),
            tax_amount=Decimal("269.82"),
            total_amount=Decimal("1768.82"),
            amount_paid=Decimal("0.00"),
            balance_due=Decimal("1768.82"),
        )
        db.add_all([inv_curr_1, inv_curr_2])
        db.commit()

        print("Successfully seeded Brightloop demo data!")
        print("Demo Accounts:")
        print("  Admin:    admin@brightloop.io    / Admin@123")
        print("  Staff:    staff@brightloop.io    / Staff@123")
        print("  Customer: customer@example.com   / Customer@123")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
