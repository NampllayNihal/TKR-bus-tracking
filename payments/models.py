from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class FeeRecord(models.Model):
    """
    IMPROVED FeeRecord with status tracking and audit trail.
    
    Changes from original:
    - Added status field (PENDING, PAID, OVERDUE)
    - Changed paid_on to DateTimeField (nullable)
    - Added payment_method field
    - Added remarks field
    - Added updated_by field for audit trail
    - Added indexes for common queries
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash Payment'),
        ('online', 'Online Payment'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    )
    
    student = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
        related_name='fee_records',
        help_text="Student this fee is for"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Fee amount in ₹"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current payment status"
    )
    due_date = models.DateField(
        help_text="Payment due date"
    )
    paid_on = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the fee was actually paid (NULL if not paid)"
    )
    payment_method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True,
        help_text="How the student paid"
    )
    remarks = models.TextField(
        blank=True,
        help_text="Any notes about this payment"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='fee_records_updated',
        help_text="Admin who last updated this record"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update time"
    )

    class Meta:
        app_label = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.student.hall_ticket} - ₹{self.amount} ({self.get_status_display()})"

    def mark_as_paid(self, method='cash', remarks='', user=None):
        """
        Mark this fee as paid.
        
        Args:
            method: Payment method
            remarks: Optional remarks
            user: Admin user who processed this
        """
        from django.utils import timezone
        
        self.status = 'paid'
        self.paid_on = timezone.now()
        self.payment_method = method
        self.remarks = remarks
        self.updated_by = user
        self.save()

    def is_overdue(self):
        """Check if payment is overdue."""
        from django.utils import timezone
        from datetime import date
        
        return (
            self.status == 'pending' 
            and self.due_date < date.today()
        )


class FeePayment(models.Model):
    """
    HISTORICAL LOG of actual payments received.
    
    Enables:
    - Full audit trail of who paid what when
    - Support for partial payments
    - Payment reconciliation
    - Receipt generation
    """
    fee_record = models.ForeignKey(
        FeeRecord,
        on_delete=models.CASCADE,
        related_name='payment_logs',
        help_text="Original fee record this payment is for"
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount actually paid in this transaction"
    )
    payment_method = models.CharField(
        max_length=15,
        choices=FeeRecord.PAYMENT_METHOD_CHOICES,
        help_text="Payment method for this transaction"
    )
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Online transaction ID or check number"
    )
    paid_on = models.DateTimeField(
        auto_now_add=True,
        help_text="When this payment was received"
    )
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Generated receipt number"
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        help_text="Admin who processed this payment"
    )
    notes = models.TextField(
        blank=True,
        help_text="Any additional notes about this payment"
    )

    class Meta:
        app_label = 'payments'
        ordering = ['-paid_on']
        indexes = [
            models.Index(fields=['fee_record', 'paid_on']),
            models.Index(fields=['paid_on']),
        ]

    def __str__(self):
        return f"Payment - ₹{self.amount_paid} on {self.paid_on.date()}"

    def save(self, *args, **kwargs):
        """Auto-generate receipt number if not set."""
        if not self.receipt_number:
            from django.utils import timezone
            self.receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)

