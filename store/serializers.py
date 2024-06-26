from rest_framework import serializers
from django.db import transaction
from .models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem, ProductImage
from decimal import Decimal
from .signals import order_created

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title']

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):

    
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # unit_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title','description', 'slug', 'inventory', 'unit_price', 'price_with_tax', 'collection', 'images']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.13)
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, CartItem):
        return CartItem.quantity * CartItem.product.unit_price


    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):

    #    print([item.quantity * item.product.unit_price for item in cart.items.all()])
       return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
        
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('The product ID does not exit.')
        return value

    def save(self, **kwargs):
        print(self.validated_data)
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            print(f"cart_item:{cart_item}")
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        
        return self.instance
    


    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        # print(instance.quantity)
        update_quantity = self.validated_data['quantity']
        instance.quantity = update_quantity

        # print(instance.id)
        # print(instance.cart)
        # print(f"after change {instance.quantity}")

        return instance
    
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class OrderItemDisplaySerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']

class OrderDisplaySerializer(serializers.ModelSerializer):
    # items = CartItemSerializer(many=True, read_only=True)
    orderitems = OrderItemDisplaySerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','orderitems', 'placed_at', 'payment_status', 'customer']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()  

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No cart with the give ID was found")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("The cart is empty")
        return cart_id


    def save(self, **kwargs):
        with transaction.atomic():
            cart_id=self.validated_data['cart_id']
            print(self.validated_data['cart_id'])
            print(self.context['user_id'])
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects \
                                        .select_related('product') \
                                        .filter(cart_id=cart_id)
            print(f"cart_item {cart_items}")
            order_items = [
                OrderItem(
                order=order,
                product=item.product,
                unit_price=item.product.unit_price,
                quantity=item.quantity
            ) for item in cart_items
            ]
            
            OrderItem.objects.bulk_create(order_items)
            print(f"order_items {order_items}")
            Cart.objects.filter(pk=cart_id).delete()
            order_created.send_robust(self.__class__, order=order)
            return order
        

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']