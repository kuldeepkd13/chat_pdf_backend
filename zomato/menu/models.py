from djongo import models
class Dish(models.Model):
    dish_id = models.AutoField(primary_key=True)
    dish_name = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    availability = models.BooleanField(default=True)

    def __str__(self):
        return self.dish_name

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    dishes = models.ManyToManyField(Dish)
    price = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('received', 'Received'),
            ('preparing', 'Preparing'),
            ('ready', 'Ready for Pickup'),
            ('delivered', 'Delivered'),
        ],
        default='received'
    )

    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
