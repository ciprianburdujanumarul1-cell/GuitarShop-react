from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from mainpage.models import Userdetail
from products.models import Product, Review, Wishlist


class ProductSerializer(serializers.ModelSerializer):
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'image', 'price', 'stock', 'is_in_stock',
            'shape', 'body', 'neck', 'grip_shape', 'fingerboard', 'fret',
            'inlay', 'scale', 'nut', 'construction', 'tuner', 'bridge',
            'pickup', 'controls', 'color',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'username', 'message', 'rating', 'created_at']


class ProductDetailSerializer(ProductSerializer):
    reviews = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'reviews', 'avg_rating', 'review_count', 'is_favorited',
        ]

    def get_reviews(self, obj):
        return ReviewSerializer(obj.reviews.order_by('-created_at'), many=True).data

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    def get_review_count(self, obj):
        return obj.reviews.count()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return Wishlist.objects.filter(user=user, product=obj).exists()


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    country = serializers.CharField(max_length=128)
    city = serializers.CharField(max_length=128)
    address = serializers.CharField(max_length=128)
    postal_code = serializers.CharField(max_length=128)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already registered")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        Userdetail.objects.create(
            user=user,
            country=validated_data['country'],
            city=validated_data['city'],
            address=validated_data['address'],
            postal_code=validated_data['postal_code'],
        )
        return user


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login with email + password instead of username, mirroring the
    original mainpage.views.l behaviour."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Swap the inherited 'username' field for 'email'
        self.fields.pop(self.username_field, None)
        self.fields['email'] = serializers.EmailField()

    def validate(self, attrs):
        from django.contrib.auth import authenticate

        email = attrs.get('email')
        password = attrs.get('password')
        user_obj = User.objects.filter(email=email).first()
        if user_obj is None:
            raise serializers.ValidationError('Invalid email or password')

        user = authenticate(username=user_obj.username, password=password)
        if user is None:
            raise serializers.ValidationError('Invalid email or password')

        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
        }
