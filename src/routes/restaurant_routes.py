from flask import Blueprint, make_response, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, set_access_cookies
from ..controllers.restaurant_controller import login_user, register_user, \
    register_restaurant, add_dish, update_dish, delete_dish, get_dish, get_dishes, get_dishes_sold
from ..utils.encrypt import create_hashed_password, validate_password
from ..utils.token import generate_token

restaurant = Blueprint('restaurant', __name__)


@restaurant.route("/register", methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    new_password = create_hashed_password(password)
    register_user(str(username), str(new_password))
    return jsonify({
        "ok": True,
        "message": "Successful user registration"
    }), 200


@restaurant.route("/login", methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    id_user_db, password_db = login_user(username)
    print("/login =>", id_user_db, password_db)
    login_value = validate_password(str(password), str(password_db))

    if login_value:
        token = generate_token(id_user_db)
        response = jsonify({"login": True, "token": token})
        set_access_cookies(response, token)
        # return jsonify({'message': 'Invalid username or password'}), 401
        #return make_response('Successful login', 200)
        return response, 200

    else:
        # return jsonify({'message': 'Invalid username or password'}), 401
        return make_response(jsonify({
            "ok": False,
            "message": "Unable to login"
        }), 403, {'Status': 'Invalid credentials'})

"""
    estas haciendo aqui lo de JWT REQUIRED
"""


@restaurant.route("/session/restaurant", methods=['POST'])
#@jwt_required()
def session_restaurant():
    user_id = get_jwt_identity()
    print("user id jwt =>", user_id)
    name_restaurant = request.json.get('name')
    #register_restaurant(name_restaurant, user_id)
    #register_restaurant(name_restaurant, 1)
    return make_response(jsonify({
        "ok": True,
        "message": "Successful restaurant registration"
    }), 200)


#@restaurant.route("/session/restaurant/:id/dish")
@restaurant.route("/session/restaurant/<int:rid>/dish", methods=['POST'])
#jwt_required
def session_restaurant_add_dish(rid):
    name_dish = request.json.get('name')
    price_dish = request.json.get('price')
    url_dish = request.json.get('url')
    status_dish = request.json.get('status')
    add_dish(name_dish, price_dish, url_dish, status_dish, rid)
    return make_response(jsonify({
        "ok": True,
        "message": "Dish added successfully"
    }), 200)


@restaurant.route("/session/restaurant/<int:rid>/dish/<int:did>", methods=['GET', 'PUT', 'DELETE'])
#@jwt_required()
def session_restaurant_update_dish(rid, did):
    if request.method == 'PUT':
        name_dish = request.json.get('name')
        price_dish = request.json.get('price')
        url_dish = request.json.get('url')
        status_dish = request.json.get('is_active_day')
        update_dish(str(name_dish), int(price_dish), str(url_dish), int(status_dish), int(rid), int(did))
        return make_response(jsonify({
            "ok": True,
            "message": "Dish updated successfully"
        }), 200)
    elif request.method == 'DELETE':
        delete_dish(int(rid), int(did))
        return make_response(jsonify({
            "ok": True,
            "message": "Dish deleted successfully"
        }), 200)
    else:
        dish = get_dish(int(rid), int(did))
        return make_response(jsonify({
            "ok": True,
            "message": "Successful dish",
            "data": dish
        }), 200)


@restaurant.route("/session/restaurant/<int:rid>/dishes", methods=['GET'])
#session/restaurant/1/dishes?day=1
#@jwt_required()
def session_restaurant_get_dishes(rid):
    day = request.args.get('day', default=None)
    dishes = get_dishes(int(rid), day)
    return make_response(jsonify({
            "ok": True,
            "message": "Restaurant dishes" if not day else "Restaurant's daily dishes",
            "data": dishes
        }), 200)


@restaurant.route("/session/restaurant/<int:rid>/buying", methods=['GET'])
def session_restaurant_buying(rid):
    dishes_buy = get_dishes_sold(int(rid))
    return make_response(jsonify({
        "ok": True,
        "message": "Dishes sold",
        "data": dishes_buy
    }), 200)
