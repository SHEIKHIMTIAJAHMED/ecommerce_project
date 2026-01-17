from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.filter(status='active')
    categories = Category.objects.all()
    
    return render(request, 'products/list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    return render(request, 'products/detail.html', {
        'product': product
    })