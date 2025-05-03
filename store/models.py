from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=0)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    retail_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price_type = models.CharField(max_length=10, choices=[('retail', 'Retail'), ('wholesale', 'Wholesale')])
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)









# from django.db import models

# class Item(models.Model):
#     name = models.CharField(max_length=100)
#     color = models.CharField(max_length=50, blank=True, null=True)
#     stock = models.IntegerField(default=0)
#     retail_price = models.DecimalField(max_digits=10, decimal_places=2)
#     wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return self.name

# class Sale(models.Model):
#     timestamp = models.DateTimeField(auto_now_add=True)
#     items = models.JSONField()  # Store cart items
#     total = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"Sale {self.id} at {self.timestamp}"