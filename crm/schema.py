import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")

from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter
from django.db import transaction
import re

class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)
    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            return CreateCustomer(customer=None, message="Email already exists")
        if input.phone and not re.match(r"^(\+\d{10,}|\d{3}-\d{3}-\d{4})$", input.phone):
            return CreateCustomer(customer=None, message="Invalid phone format")
        customer = Customer.objects.create(name=input.name, email=input.email, phone=input.phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created = []
        errors = []
        with transaction.atomic():
            for idx, data in enumerate(input):
                if Customer.objects.filter(email=data.email).exists():
                    errors.append(f"Row {idx+1}: Email already exists")
                    continue
                if data.phone and not re.match(r"^(\+\d{10,}|\d{3}-\d{3}-\d{4})$", data.phone):
                    errors.append(f"Row {idx+1}: Invalid phone format")
                    continue
                customer = Customer(name=data.name, email=data.email, phone=data.phone)
                customer.save()
                created.append(customer)
        return BulkCreateCustomers(customers=created, errors=errors)

class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)
    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product.objects.create(name=input.name, price=input.price, stock=input.stock or 0)
        return CreateProduct(product=product)

class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)
    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")
        products = Product.objects.filter(pk__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise Exception("One or more product IDs are invalid")
        if not products:
            raise Exception("At least one product must be selected")
        total_amount = sum([p.price for p in products])
        order = Order.objects.create(customer=customer, total_amount=total_amount, order_date=input.order_date)
        order.products.set(products)
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated = []
        for product in low_stock_products:
            product.stock += 10
            product.save()
            updated.append(product)
        return UpdateLowStockProducts(
            success=True,
            message=f"Updated {len(updated)} products",
            updated_products=updated
        )

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(root, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query, mutation=Mutation)
