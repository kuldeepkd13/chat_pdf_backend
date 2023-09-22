import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bson import Decimal128  # Import Decimal128 from bson
from .models import Dish , Order

@csrf_exempt
def create(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)

            dish_name = data.get('dish_name')
            price = data.get('price')  
            availability = data.get('availability')

            # Perform basic validation if required

            dish = Dish(dish_name=dish_name, price=price, availability=availability)
            dish.save()

            return JsonResponse({'message': 'Dish created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

def view(request):
    dishes = Dish.objects.all()
    dish_list = []

    for dish in dishes:
        dish_data = {
            "dish_id": dish.dish_id,
            "dish_name": dish.dish_name,
            "price": float(dish.price), 
            "availability": dish.availability,
        }
        dish_list.append(dish_data)

    return JsonResponse({"dishes": dish_list})

def view_dish(request, dish_id):
    try:
        dish = Dish.objects.get(dish_id=dish_id)
        dish_data = {
            "dish_id": dish.dish_id,
            "dish_name": dish.dish_name,
            "price": float(dish.price), 
            "availability": dish.availability,
        }
        return JsonResponse(dish_data)
    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Dish not found'}, status=404)

@csrf_exempt
def update_availability(request, dish_id):
    try:
        # Find the dish by dish_id
        dish = Dish.objects.get(dish_id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Dish not found'}, status=404)

    if  request.method == 'PATCH':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)

            availability = data.get('availability')
            
            if availability is not None:
                dish.availability = availability
                dish.save()
                return JsonResponse({'message': 'Availability updated successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid availability data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': f'Only  PATCH requests are allowed for dish {dish_id}'}, status=405)


@csrf_exempt
def delete_dish(request, dish_id):
    try:
        dish = Dish.objects.get(dish_id=dish_id)
    except Dish.DoesNotExist:
        return JsonResponse({'error': 'Dish not found'}, status=404)

    if request.method == 'DELETE':
        dish.delete()
        return JsonResponse({'message': 'Dish deleted successfully'}, status=204)

    return JsonResponse({'error': f'Only DELETE requests are allowed for dish {dish_id}'}, status=405)


@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)

            customer_name = data.get('customer_name')
            dish_ids = data.get('dishes', [])
            status = data.get('status', 'received')

            # Find dishes based on the provided dish IDs
            dishes = Dish.objects.filter(dish_id__in=dish_ids)

            # Calculate the total price based on the selected dishes' prices
            total_price = sum(float(dish.price) for dish in dishes)

            # Create the order with the calculated total price
            order = Order(customer_name=customer_name, status=status, price=total_price)
            order.save()
            order.dishes.set(dishes)

            return JsonResponse({'message': 'Order created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)



def get_orders(request):
    orders = Order.objects.all()
    order_list = []

    for order in orders:
        order_data = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "status": order.status,
            'price': order.price,
            "dishes": [dish.dish_id for dish in order.dishes.all()]
        }
        order_list.append(order_data)

    return JsonResponse({"orders": order_list})

@csrf_exempt
def update_order_status(request, order_id):
    if request.method == 'PATCH':
        try:
            # Load the JSON data from the request body
            data = json.loads(request.body)

            new_status = data.get('status')

            # Find the order based on the provided order_id
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({'error': f'Order with order_id {order_id} not found'}, status=404)

            # Update the order status
            order.status = new_status
            order.save()

            return JsonResponse({'message': 'Order status updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Only PATCH requests are allowed'}, status=405)

# print(".................................................")
#             print("data" , data)

def menu(request):
    data = {"message": "hello"}
    return JsonResponse(data)