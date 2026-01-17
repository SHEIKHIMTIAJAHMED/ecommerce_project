from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from .models import Payment
from .services import PaymentProcessor

@login_required
def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.status == 'paid':
        messages.warning(request, 'This order has already been paid.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        provider = request.POST.get('provider')
        
        for item in order.items.all():
            if item.product.stock < item.quantity:
                messages.error(request, f'Not enough stock for {item.product.name}. Only {item.product.stock} left.')
                return redirect('order_detail', order_id=order.id)
        
        result = PaymentProcessor.process_payment(order, provider)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('payment_success', payment_id=result['payment_id'])
        else:
            messages.error(request, result['message'])
            return redirect('order_detail', order_id=order.id)
    
    return render(request, 'payments/checkout.html', {
        'order': order
    })

@login_required
def payment_success(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
       
    if payment.status == 'success':
        for item in payment.order.items.all():
            if item.product.stock <= 0:
                item.product.stock = 0
                item.product.save()
    
    return render(request, 'payments/success.html', {
        'order': payment.order,
        'payment': payment
    })

@login_required
def payment_failed(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.order.user != request.user:
        messages.error(request, 'You are not authorized to view this payment.')
        return redirect('order_list')
    
    return render(request, 'payments/failed.html', {
        'order': payment.order,
        'payment': payment
    })