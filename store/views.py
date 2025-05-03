import pandas as pd
from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
import json

def store(request):
    products = Product.objects.all()
    return render(request, 'store/index.html', {'products': products})

@login_required
def manage_stock(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            retail_price = data.get('retail_price', '')
            wholesale_price = data.get('wholesale_price', '')
            stock = data.get('stock', '')

            errors = []
            if not name: errors.append("Product name is required")
            if not retail_price: errors.append("Retail price is required")
            if not wholesale_price: errors.append("Wholesale price is required")
            if not stock: errors.append("Stock quantity is required")

            if errors:
                return JsonResponse({'error': "; ".join(errors)}, status=400)

            try:
                retail_price = float(retail_price)
                wholesale_price = float(wholesale_price)
                stock = int(float(stock))
                if retail_price < 0: errors.append("Retail price must be positive")
                if wholesale_price < 0: errors.append("Wholesale price must be positive")
                if stock < 0: errors.append("Stock must be positive")
                if errors: return JsonResponse({'error': "; ".join(errors)}, status=400)
            except ValueError:
                return JsonResponse({'error': 'Invalid number format for prices or stock'}, status=400)

            product, created = Product.objects.get_or_create(name=name)
            product.retail_price = retail_price  # Update price
            product.wholesale_price = wholesale_price  # Update price
            product.stock += stock  # Add to existing stock
            product.save()

            products = Product.objects.all().values('id', 'name', 'retail_price', 'wholesale_price', 'stock')
            return JsonResponse({'message': 'Product saved successfully', 'products': list(products)}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def upload_products(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        excel_file = request.FILES['excel_file']
        try:
            df = pd.read_excel(excel_file)
            print("Excel DataFrame:", df.to_dict())
            print("Column names in Excel:", list(df.columns))

            df.columns = [col.lower().strip() for col in df.columns]
            required_columns = {'name', 'retail_price', 'wholesale_price', 'stock'}
            if not all(col in df.columns for col in required_columns):
                missing_cols = required_columns - set(df.columns)
                return JsonResponse({'error': f"Missing required columns: {missing_cols}"}, status=400)

            errors = []
            for index, row in df.iterrows():
                name = str(row.get('name', '')).strip()
                retail_price = row.get('retail_price')
                wholesale_price = row.get('wholesale_price')
                stock = row.get('stock')

                print(f"Row {index + 1} raw data:", name, retail_price, wholesale_price, stock)
                retail_price = float(retail_price) if retail_price is not None else None
                wholesale_price = float(wholesale_price) if wholesale_price is not None else None
                stock = float(stock) if stock is not None else 0.0  # Default to 0 if None

                print(f"Row {index + 1} after conversion:", name, retail_price, wholesale_price, stock)
                if not all([name, retail_price, wholesale_price, stock is not None]):
                    errors.append(f"Row {index + 1}: Missing required fields (name: {name}, retail_price: {retail_price}, wholesale_price: {wholesale_price}, stock: {stock})")
                    continue

                try:
                    retail_price = float(retail_price)
                    wholesale_price = float(wholesale_price)
                    stock = int(float(stock))
                    print(f"Row {index + 1} final stock value:", stock)
                    if retail_price < 0 or wholesale_price < 0 or stock < 0:
                        errors.append(f"Row {index + 1}: Prices and stock must be positive")
                        continue
                except ValueError:
                    errors.append(f"Row {index + 1}: Invalid number format")
                    continue

                product, created = Product.objects.get_or_create(name=name)
                print(f"Product {name} before update: stock = {product.stock}")
                product.retail_price = retail_price
                product.wholesale_price = wholesale_price
                if product.stock is None:  # Ensure stock is never None
                    product.stock = 0
                product.stock += stock
                print(f"Product {name} after update: stock = {product.stock}")
                product.save()

            if errors:
                return JsonResponse({'error': "; ".join(errors)}, status=400)
            
            products = Product.objects.all().values('id', 'name', 'retail_price', 'wholesale_price', 'stock')
            return JsonResponse({'message': 'Products updated successfully', 'products': list(products)}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Error processing file: {str(e)}'}, status=400)
    return render(request, 'store/index.html', {'error': 'No file uploaded'})
def checkout(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart = data
        order = Order.objects.create(user=request.user)
        total = 0
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            quantity = int(item['qty'])
            price = float(item['price'])
            if product.stock < quantity:
                return JsonResponse({'error': f"Insufficient stock for {product.name}"}, status=400)
            product.stock -= quantity
            product.save()
            price_type = 'retail' if price == float(product.retail_price) else 'wholesale'
            OrderItem.objects.create(order=order, product=product, price_type=price_type, quantity=quantity, price=price)
            total += quantity * price
        order.total = total
        order.save()
        return JsonResponse({'message': 'Checkout successful!'})
    
@login_required
def export_products(request):
    products = Product.objects.all().values('name', 'retail_price', 'wholesale_price', 'stock')
    df = pd.DataFrame(list(products))
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=products_export.xlsx'
    df.to_excel(response, index=False)
    return response    