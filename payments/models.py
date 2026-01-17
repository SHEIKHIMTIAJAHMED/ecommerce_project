from django.db import models
from django.db import transaction
from orders.models import Order

class Payment(models.Model):
    PROVIDER_CHOICES = (
        ('stripe', 'Stripe'),
        ('bkash', 'bKash'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    raw_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
    
    def __str__(self):
        return f"{self.provider} - {self.transaction_id}"
    
    def mark_as_successful(self):
        """if payment successful than update stock"""
        with transaction.atomic():
            self.status = 'success'
            self.save()
            
            self.order.status = 'paid'
            self.order.save()
            
            for item in self.order.items.all():
                product = item.product
                if product.stock >= item.quantity:
                    product.stock -= item.quantity
                    product.save()
                else:
                    raise ValueError(f"Not enough stock for {product.name}")
    
    def mark_as_failed(self):
        """If payment failed"""
        self.status = 'failed'
        self.save()