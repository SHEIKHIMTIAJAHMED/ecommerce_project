from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from products.models import Product
from .models import Order, OrderItem

@login_required
def create_order(request):
    """Simple order creation"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                items_to_order = []
                for key, value in request.POST.items():
                    if key.startswith('product_'):
                        product_id = key.replace('product_', '')
                        quantity = int(value)
                        
                        if quantity > 0:
                            product = Product.objects.get(id=product_id)
                            
                            if product.stock < quantity:
                                messages.error(request, 
                                    f'Not enough stock for {product.name}. Only {product.stock} available.')
                                return redirect('create_order')
                            
                            items_to_order.append({
                                'product': product,
                                'quantity': quantity,
                                'price': product.price
                            })
                
                if not items_to_order:
                    messages.warning(request, 'Please select at least one product.')
                    return redirect('create_order')
                
                # Create order
                total = sum(item['price'] * item['quantity'] for item in items_to_order)
                order = Order.objects.create(user=request.user, total_amount=total, status='pending')
                
                # Create order items
                for item_data in items_to_order:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],
                        quantity=item_data['quantity'],
                        price=item_data['price'],
                        subtotal=item_data['price'] * item_data['quantity']
                    )
                
                messages.success(request, 'Order created successfully!')
                return redirect('payment_checkout', order_id=order.id)
        
        except Exception as e:
            messages.error(request, f'Error creating order: {str(e)}')
    
    products = Product.objects.filter(status='active', stock__gt=0)
    return render(request, 'orders/create.html', {'products': products})

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {'order': order})