#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, jsonify, request
from flask_restful import Api
import os
from sqlalchemy.exc import IntegrityError

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Routes

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([
        {"id": restaurant.id, "name": restaurant.name, "address": restaurant.address}
        for restaurant in restaurants
    ]), 200


# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }), 200


# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([
        {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients}
        for pizza in pizzas
    ]), 200


# GET /pizzas/<int:id>
@app.route("/pizzas/<int:id>", methods=["GET"])
def get_pizza(id):
    pizza = db.session.get(Pizza, id)
    if not pizza:
        return jsonify({"error": "Pizza not found"}), 404

    return jsonify({"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients}), 200


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    # Input validation
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if price is None or pizza_id is None or restaurant_id is None:
        return jsonify({"errors": ["validation errors"]}), 400

    if not (1 <= price <= 30):
        return jsonify({"errors": ["validation errors"]}), 400

    pizza = db.session.get(Pizza, pizza_id)
    restaurant = db.session.get(Restaurant, restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant_id": restaurant_pizza.restaurant_id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400
    

    #adding new resturant
@app.route('/restaurants_pizza', methods=['POST'])
def create_restaurant():
    data = request.get_json()

  
    name = data.get('name')
    address = data.get('address')
    restaurant_pizzas_data = data.get('restaurant_pizzas', [])

    # Validate required fields
    if not name or not address:
        return jsonify({"errors": ["'name' and 'address' are required"]}), 400

    # Create the restaurant instance
    restaurant = Restaurant(name=name, address=address)
    db.session.add(restaurant)
    db.session.commit()  

    # Process nested restaurant_pizzas data
    for rp_data in restaurant_pizzas_data:
        price = rp_data.get('price')
        pizza_data = rp_data.get('pizza')
        if not pizza_data or 'id' not in pizza_data:
            return jsonify({"errors": ["Pizza data with an 'id' is required for each restaurant pizza"]}), 400

        # Option 1: If the pizza already exists in your database:
        pizza = Pizza.query.get(pizza_data['id'])
        if not pizza:
            # Optionally, you might create a new Pizza if it doesn't exist
            pizza = Pizza(name=pizza_data.get('name'), ingredients=pizza_data.get('ingredients'))
            db.session.add(pizza)
            db.session.commit()

        # Option 2: Alternatively, if you expect the pizza to exist, return an error if not found.
        # if not pizza:
        #     return jsonify({"errors": [f"Pizza with id {pizza_data['id']} not found"]}), 400

        # Validate price if needed
        if price is None or not (1 <= price <= 30):
            return jsonify({"errors": ["Price is required and must be between 1 and 30"]}), 400

        # Create the RestaurantPizza association
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza.id, restaurant_id=restaurant.id)
        db.session.add(restaurant_pizza)

    db.session.commit()

    # Return the created restaurant (and optionally the associated pizzas)
    return jsonify({
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                }
            }
            for rp in restaurant.restaurant_pizzas  # Assuming a relationship is set up in your model
        ]
    }), 201

if __name__ == "__main__":
    app.run(port=5555, debug=True)
