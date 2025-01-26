from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# Restaurant has many Pizzas through RestaurantPizza:
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationship with RestaurantPizza -- 
    #restaurant model has relationship with pizza thru the restuarantpizza model
    restaurant_pizzas = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"
    )

    # Proxy relationship to directly access pizzas through the restaurant
    # pizzas = association_proxy("restaurant_pizzas", "pizza")

    # Serialization rules to avoid infinite recursion when serializing data
    # serialize_only = ("id", "name", "address")
    serialize_rules = ("-restaurant_pizzas.restaurant",)

    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "name": self.name,
    #         "address": self.address,
    #         "restaurant_pizzas": [
    #             {
    #                 "id": rp.id,
    #                 "price": rp.price,
    #                 "pizza_id": rp.pizza_id,
    #                 "restaurant_id": rp.restaurant_id,
    #                 "pizza": {
    #                     "id": rp.pizza.id,
    #                     "name": rp.pizza.name,
    #                     "ingredients": rp.pizza.ingredients,
    #                 },
    #             }
    #             for rp in self.restaurant_pizzas
    #         ],
    #     }
    def __repr__(self):
        return f"<Restaurant {self.name}>"

# Pizza has many Restaurants through RestaurantPizza:
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # restaurant_pizzas relationship in the Pizza model.

    restaurant_pizzas = relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"
    )

    # Serialization rules
    serialize_rules = ("-restaurant_pizzas.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # RestaurantPizza model has foreign keys restaurant_id and pizza_id, 
   
    restaurant_id = db.Column(db.Integer, ForeignKey("restaurants.id"), nullable=False)
    pizza_id = db.Column(db.Integer, ForeignKey("pizzas.id"), nullable=False)

    #relationships with the Restaurant and Pizza models is formed through these foreign keys
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")

    # Serialization rules
    serialize_rules = ("-restaurant.restaurant_pizzas", "-pizza.restaurant_pizzas")

    # Validation for price to ensure the price of pizza is between 1-30
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
