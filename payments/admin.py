from django.contrib import admin
from django.utils.html import format_html
from .models import FeeRecord, FeePayment


@admin.register(FeeRecord)
class FeeRecordAdmin(admin.ModelAdmin):
    list_display = ['get_student_id', 'amount', 'status_badge', 'due_date', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'due_date', 'created_at']
    search_fields = ['student__hall_ticket', 'student__user__first_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Student & Amount', {
            'fields': ('student', 'amount'),
        }),
        ('Payment Status', {
            'fields': ('status', 'payment_method', 'due_date'),
        }),
        ('Payment Record', {
            'fields': ('paid_on', 'updated_by'),
        }),
        ('Additional Info', {
            'fields': ('remarks',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_overdue', 'mark_as_cancelled']
    
    def get_student_id(self, obj):
        return obj.student.hall_ticket
    get_student_id.short_description = 'Student'
    
    def status_badge(self, obj):
        """Display status with color coding."""
        colors = {
            'pending': '#FFA500',  # Orange
            'paid': '#00AA00',     # Green
            'overdue': '#FF0000',  # Red
            'cancelled': '#888888', # Gray
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def mark_as_paid(self, request, queryset):
        """Custom action to mark fees as paid."""
        updated = queryset.update(status='paid')
        self.message_user(request, f'{updated} fee(s) marked as paid.')
    mark_as_paid.short_description = 'Mark selected as paid'
    
    def mark_as_overdue(self, request, queryset):
        """Custom action to mark fees as overdue."""
        updated = queryset.filter(status='pending').update(status='overdue')
        self.message_user(request, f'{updated} fee(s) marked as overdue.')
    mark_as_overdue.short_description = 'Mark selected as overdue'
    
    def mark_as_cancelled(self, request, queryset):
        """Custom action to mark fees as cancelled."""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} fee(s) marked as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected as cancelled'


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'get_student', 'amount_paid', 'payment_method', 'paid_on', 'processed_by']
    list_filter = ['payment_method', 'paid_on', 'processed_by']
    search_fields = ['receipt_number', 'fee_record__student__hall_ticket', 'reference_id']
    readonly_fields = ['paid_on', 'receipt_number']
    date_hierarchy = 'paid_on'
    
    fieldsets = (
        ('Fee Record', {
            'fields': ('fee_record',),
        }),
        ('Payment Details', {
            'fields': ('amount_paid', 'payment_method', 'reference_id'),
        }),
        ('Receipt & Processing', {
            'fields': ('receipt_number', 'paid_on', 'processed_by'),
        }),
        ('Notes', {
            'fields': ('notes',),
        }),
    )
    
    def get_student(self, obj):
        return obj.fee_record.student.hall_ticket
    get_student.short_description = 'Student'
    
    def save_model(self, request, obj, form, change):
        """Auto-set processed_by to current user."""
        if not obj.processed_by:
            obj.processed_by = request.user
        super().save_model(request, obj, form, change)

