"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import date, datetime, timedelta
from data_layer.model.definition.cashier_performance_target import CashierPerformanceTarget
from data_layer.model.definition.cashier import Cashier
from data_layer.model.definition.store import Store


def _insert_cashier_performance_targets(session, admin_cashier_id: str):
    """
    Insert initial cashier performance targets if not exists
    """
    # Check if targets already exist
    existing_targets = session.query(CashierPerformanceTarget).first()
    if existing_targets:
        print("✓ Cashier performance targets already exist, skipping insertion")
        return

    # Get admin cashier and default store
    admin_cashier = session.query(Cashier).filter(Cashier.user_name == "admin").first()
    default_store = session.query(Store).first()
    
    if not admin_cashier or not default_store:
        print("✗ Admin cashier or default store not found, skipping performance targets insertion")
        return
    
    # Sample performance targets
    performance_targets = [
        # Daily targets
        CashierPerformanceTarget(
            fk_cashier_id=admin_cashier.id,
            fk_store_id=default_store.id,
            target_type="INDIVIDUAL",
            target_period="DAILY",
            target_start_date=date.today(),
            target_end_date=date.today() + timedelta(days=30),
            target_year=date.today().year,
            target_month=date.today().month,
            target_total_sales=5000,  # £50.00 in pence
            target_transactions_count=100,
            target_items_sold=200,
            target_customers_served=100,
            target_average_transaction_amount=50,  # £0.50 in pence
            target_transactions_per_hour=15.0,
            target_sales_per_hour=750,  # £7.50 per hour in pence
            target_items_per_hour=25.0,
            target_customers_per_hour=12.5,
            target_average_transaction_time=240.0,  # 4 minutes in seconds
            target_working_hours=8.0,
            target_void_rate=2.0,  # Maximum 2%
            target_return_rate=1.0,  # Maximum 1%
            target_error_rate=0.5,  # Maximum 0.5%
            target_accuracy_score=95.0,  # Minimum 95%
            target_customer_satisfaction=4.0,  # Minimum 4 out of 5
            target_productivity_score=85.0,
            target_efficiency_score=80.0,
            target_service_quality_score=90.0,
            target_punctuality_score=95.0,
            target_attendance_rate=95.0,
            target_break_compliance=90.0,
            max_late_arrivals=2,
            max_early_departures=1,
            target_cash_handling_accuracy=99.0,
            target_card_payment_processing=98.0,
            target_digital_payment_adoption=30.0,
            target_difficulty_level="MEDIUM",
            target_priority="HIGH",
            is_mandatory=True,
            is_achievable=True,
            incentive_type="BONUS",
            incentive_amount=500,  # £5.00 bonus in pence
            incentive_description="£5.00 bonus for cashiers meeting daily targets",
            target_status="ACTIVE",
            review_frequency="DAILY",
            next_review_date=date.today() + timedelta(days=1),
            target_description="Daily basic performance targets",
            target_rationale="Increase cashier productivity and ensure customer satisfaction",
            success_criteria="Achieve minimum 80% of all targets",
            measurement_method="Automatic system tracking and daily reporting",
            fk_cashier_create_id=admin_cashier.id,
            fk_cashier_update_id=admin_cashier.id
        ),
        
        # Weekly targets
        CashierPerformanceTarget(
            fk_cashier_id=admin_cashier.id,
            fk_store_id=default_store.id,
            target_type="INDIVIDUAL",
            target_period="WEEKLY",
            target_start_date=date.today(),
            target_end_date=date.today() + timedelta(weeks=4),
            target_year=date.today().year,
            target_month=date.today().month,
            target_week=date.today().isocalendar()[1],
            target_total_sales=35000,  # £350.00 in pence
            target_transactions_count=700,
            target_items_sold=1400,
            target_customers_served=700,
            target_average_transaction_amount=50,  # £0.50 in pence
            target_transactions_per_hour=15.0,
            target_sales_per_hour=750,  # £7.50 per hour in pence
            target_items_per_hour=25.0,
            target_customers_per_hour=12.5,
            target_average_transaction_time=240.0,
            target_working_hours=40.0,
            target_void_rate=2.0,
            target_return_rate=1.0,
            target_error_rate=0.5,
            target_accuracy_score=95.0,
            target_customer_satisfaction=4.0,
            target_productivity_score=85.0,
            target_efficiency_score=80.0,
            target_service_quality_score=90.0,
            target_punctuality_score=95.0,
            target_attendance_rate=95.0,
            target_break_compliance=90.0,
            max_late_arrivals=1,
            max_early_departures=0,
            target_cash_handling_accuracy=99.0,
            target_card_payment_processing=98.0,
            target_digital_payment_adoption=30.0,
            target_training_hours=2.0,
            target_skill_assessments=1,
            target_difficulty_level="MEDIUM",
            target_priority="HIGH",
            is_mandatory=True,
            is_achievable=True,
            incentive_type="RECOGNITION",
            incentive_description="Certificate of recognition for cashiers meeting weekly targets",
            target_status="ACTIVE",
            review_frequency="WEEKLY",
            next_review_date=date.today() + timedelta(weeks=1),
            target_description="Weekly performance and development targets",
            target_rationale="Ensure continuous improvement and consistent performance",
            success_criteria="Achieve minimum 85% of weekly targets",
            measurement_method="Weekly performance reports and assessments",
            fk_cashier_create_id=admin_cashier.id,
            fk_cashier_update_id=admin_cashier.id
        ),
        
        # Monthly targets
        CashierPerformanceTarget(
            fk_cashier_id=admin_cashier.id,
            fk_store_id=default_store.id,
            target_type="INDIVIDUAL",
            target_period="MONTHLY",
            target_start_date=date.today(),
            target_end_date=date.today() + timedelta(days=90),
            target_year=date.today().year,
            target_month=date.today().month,
            target_total_sales=150000,  # £1500.00 in pence
            target_transactions_count=3000,
            target_items_sold=6000,
            target_customers_served=3000,
            target_average_transaction_amount=50,  # £0.50 in pence
            target_transactions_per_hour=15.0,
            target_sales_per_hour=750,  # £7.50 per hour in pence
            target_items_per_hour=25.0,
            target_customers_per_hour=12.5,
            target_average_transaction_time=240.0,
            target_working_hours=160.0,
            target_void_rate=2.0,
            target_return_rate=1.0,
            target_error_rate=0.5,
            target_accuracy_score=95.0,
            target_customer_satisfaction=4.0,
            target_productivity_score=85.0,
            target_efficiency_score=80.0,
            target_service_quality_score=90.0,
            target_punctuality_score=95.0,
            target_attendance_rate=95.0,
            target_break_compliance=90.0,
            max_late_arrivals=3,
            max_early_departures=1,
            target_cash_handling_accuracy=99.0,
            target_card_payment_processing=98.0,
            target_digital_payment_adoption=35.0,
            target_training_hours=8.0,
            target_skill_assessments=2,
            target_certification_completion=100.0,
            target_team_support_score=85.0,
            target_knowledge_sharing=2,
            target_difficulty_level="HARD",
            target_priority="CRITICAL",
            is_mandatory=True,
            is_achievable=True,
            incentive_type="BONUS",
            incentive_amount=2500,  # £25.00 bonus in pence
            incentive_description="£25.00 bonus and promotion evaluation for cashiers meeting monthly targets",
            penalty_type="TRAINING",
            penalty_description="Additional training program for cashiers not meeting targets",
            target_status="ACTIVE",
            review_frequency="WEEKLY",
            next_review_date=date.today() + timedelta(weeks=1),
            target_description="Monthly comprehensive performance and development targets",
            target_rationale="Long-term performance improvement and career development",
            success_criteria="Achieve minimum 90% of monthly targets",
            measurement_method="Monthly performance evaluation and 360-degree feedback",
            fk_cashier_create_id=admin_cashier.id,
            fk_cashier_update_id=admin_cashier.id
        ),
        
        # Yearly targets
        CashierPerformanceTarget(
            fk_cashier_id=admin_cashier.id,
            fk_store_id=default_store.id,
            target_type="INDIVIDUAL",
            target_period="YEARLY",
            target_start_date=date.today(),
            target_end_date=date.today() + timedelta(days=365),
            target_year=date.today().year,
            target_total_sales=1800000,  # £18000.00 in pence
            target_transactions_count=36000,
            target_items_sold=72000,
            target_customers_served=36000,
            target_average_transaction_amount=50,  # £0.50 in pence
            target_transactions_per_hour=15.0,
            target_sales_per_hour=750,  # £7.50 per hour in pence
            target_items_per_hour=25.0,
            target_customers_per_hour=12.5,
            target_average_transaction_time=240.0,
            target_working_hours=2000.0,
            target_void_rate=2.0,
            target_return_rate=1.0,
            target_error_rate=0.5,
            target_accuracy_score=95.0,
            target_customer_satisfaction=4.0,
            target_productivity_score=85.0,
            target_efficiency_score=80.0,
            target_service_quality_score=90.0,
            target_punctuality_score=95.0,
            target_attendance_rate=95.0,
            target_break_compliance=90.0,
            max_late_arrivals=12,
            max_early_departures=6,
            target_cash_handling_accuracy=99.0,
            target_card_payment_processing=98.0,
            target_digital_payment_adoption=40.0,
            target_training_hours=40.0,
            target_skill_assessments=12,
            target_certification_completion=100.0,
            target_team_support_score=90.0,
            target_knowledge_sharing=12,
            target_mentoring_hours=20.0,
            target_difficulty_level="CHALLENGING",
            target_priority="CRITICAL",
            is_mandatory=True,
            is_achievable=True,
            incentive_type="PROMOTION",
            incentive_amount=10000,  # £100.00 bonus in pence
            incentive_description="Promotion and £100.00 bonus for cashiers meeting yearly targets",
            target_status="ACTIVE",
            review_frequency="MONTHLY",
            next_review_date=date.today() + timedelta(days=30),
            target_description="Yearly strategic performance and career development targets",
            target_rationale="Long-term career planning and organizational alignment",
            success_criteria="Achieve minimum 95% of yearly targets",
            measurement_method="Annual performance evaluation and career planning meetings",
            fk_cashier_create_id=admin_cashier.id,
            fk_cashier_update_id=admin_cashier.id
        )
    ]
    
    try:
        # Insert all targets
        for target in performance_targets:
            session.add(target)
        
        session.commit()
        print(f"✓ Inserted {len(performance_targets)} cashier performance targets")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error inserting performance targets: {e}")
        raise 