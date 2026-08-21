from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    shape=models.CharField(max_length=100)
    body=models.CharField(max_length=100)
    neck=models.CharField(max_length=100)
    grip_shape=models.CharField(max_length=100)
    fingerboard=models.CharField(max_length=100)
    fret=models.CharField(max_length=100)
    inlay=models.CharField(max_length=100)
    scale=models.CharField(max_length=200)
    nut=models.CharField(max_length=100)
    construction=models.CharField(max_length=100)
    tuner=models.CharField(max_length=100)
    bridge=models.CharField(max_length=100)
    pickup=models.CharField(max_length=100)
    controls=models.CharField(max_length=100)
    color=models.CharField(max_length=100)
    @property
    def is_in_stock(self):
        return self.stock > 0
    def __str__(self):
        return self.name

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # prevents duplicate favorites

    def __str__(self):
        return f"{self.user.username} ♥ {self.product.name}"  

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    username = models.CharField(max_length=100)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username}: {self.message[:30]} ({self.rating}★)"