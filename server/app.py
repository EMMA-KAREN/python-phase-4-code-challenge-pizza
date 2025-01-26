#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask,jsonify, request, make_response
from flask_restful import Api, Resource
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

#routes
# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    # Return only basic details for all restaurants
    return jsonify([
        {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address
        }
        for restaurant in restaurants
    ]), 200

# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    # Return full details, including nested restaurant_pizzas and pizzas
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
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return "", 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    # Return only the specified fields for each pizza
    return jsonify([
        {
            "id": pizza.id,
            "name": pizza.name,
            "ingredients": pizza.ingredients
        }
        for pizza in pizzas
    ]), 200

@app.route("/pizzas/<int:id>", methods=["GET"])
def get_pizza(id):
    pizza = Pizza.query.get(id)
    if not pizza:
        return jsonify({"error": "Pizza not found"}), 404

    return jsonify({
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    }), 200


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (1 <= price <= 30):
        return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"errors": ["Invalid pizza_id or restaurant_id"]}), 400

    try:
        restaurant_pizza = RestaurantPizza(
            price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        return jsonify(restaurant_pizza.to_dict()), 201
    except IntegrityError:
        return jsonify({"errors": ["Failed to create RestaurantPizza"]}), 400



# @app.route("/restaurants", methods=["POST"])
# def create_restaurant():
#     data = request.get_json()

#     # Extract restaurant data
#     address = data.get("address")
#     name = data.get("name")
#     restaurant_pizzas_data = data.get("restaurant_pizzas", [])

#     # Validate basic restaurant fields
#     if not address or not name:
#         return jsonify({"errors": ["Address and Name are required"]}), 400

#     try:
#         # Create and save the Restaurant
#         restaurant = Restaurant(address=address, name=name)
#         db.session.add(restaurant)
#         db.session.flush()  # Get the restaurant's ID before committing

#         # Create associated RestaurantPizza and Pizza records
#         for rp_data in restaurant_pizzas_data:
#             price = rp_data.get("price")
#             pizza_data = rp_data.get("pizza", {})

#             # Validate price range
#             if not (1 <= price <= 30):
#                 return jsonify({"errors": ["Price must be between 1 and 30"]}), 400

#             # Get or create the Pizza
#             pizza = Pizza.query.get(pizza_data.get("id"))
#             if not pizza:
#                 pizza = Pizza(
#                     name=pizza_data.get("name"),
#                     ingredients=pizza_data.get("ingredients"),
#                 )
#                 db.session.add(pizza)
#                 db.session.flush()

#             # Create the RestaurantPizza
#             restaurant_pizza = RestaurantPizza(
#                 price=price, restaurant_id=restaurant.id, pizza_id=pizza.id
#             )
#             db.session.add(restaurant_pizza)

#         # Commit all changes
#         db.session.commit()

#         # Return the created restaurant with nested data
#         return jsonify(restaurant.to_dict()), 201

#     except IntegrityError:
#         db.session.rollback()
#         return jsonify({"errors": ["Failed to create Restaurant or related entities"]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)
