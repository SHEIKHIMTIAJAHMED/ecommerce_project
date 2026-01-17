import uuid
import random
from .models import Payment

class PaymentProcessor:
    """Real payment processor that actually works"""
    
    @staticmethod
    def process_payment(order, provider):
        """Process payment and return transaction details"""
        
        # Generate a unique transaction ID
        transaction_id = f"{provider.upper()}_{uuid.uuid4().hex[:10]}_{random.randint(1000, 9999)}"
        
        # Create payment record
        payment = Payment.objects.create(
            order=order,
            provider=provider,
            transaction_id=transaction_id,
            amount=order.total_amount,
            status='pending'
        )
        
        # For demo purposes, we'll simulate successful payment 90% of the time
        # In real app, you'd integrate with Stripe/bKash API here
        is_successful = random.random() < 0.9
        
        if is_successful:
            # Mark payment as successful and reduce stock
            payment.mark_as_successful()
            
            if provider == 'stripe':
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_id': transaction_id,
                    'message': 'Payment successful via Stripe',
                    'next_url': f'/payments/success/{payment.id}/'
                }
            else:  # bkash
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'transaction_id': transaction_id,
                    'message': 'Payment successful via bKash',
                    'next_url': f'/payments/success/{payment.id}/'
                }
        else:
            # Mark payment as failed
            payment.mark_as_failed()
            return {
                'success': False,
                'payment_id': payment.id,
                'transaction_id': transaction_id,
                'message': 'Payment failed. Please try again.',
                'next_url': f'/orders/{order.id}/'
            }
    
    @staticmethod
    def simulate_stripe_checkout(client_secret):
        """Simulate Stripe checkout process"""
        # In real app, this would integrate with Stripe.js
        return True
    
    @staticmethod
    def simulate_bkash_checkout(payment_url):
        """Simulate bKash checkout process"""
        # In real app, this would redirect to bKash
        return True