from app.blueprints.customers import customers_bp
from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Customers, db
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required
from werkzeug.security import check_password_hash, generate_password_hash


@customers_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = login_schema.load(request.json)
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting name and password'})
    
    query = select(Customers).where(Customers.name == credentials['name'])
    customer = db.session.execute(query).scalar_one_or_none() # Query customer table for a customer with this customername
    
    if customer and check_password_hash(customer.password, credentials['password']):
        auth_token = encode_token(customer.id)
        
        response = {
            'status': 'success',
            'message': 'Successfully Logged in',
            'auth_token': auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'messages': 'Invalid name or password'})

#CREATE customer ROUTE
@customers_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
@limiter.limit("3 per hour") # A client can only attempt to make 3 customers per hour
def create_customer():
    try:
        data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    taken = db.session.query(Customers).where(Customers.email==data['email']).first()
    if taken: #Checks if I got a customer from the query
        return jsonify({'message': 'email is taken'}), 400
    
    data['password'] = generate_password_hash(data['password']) #resetting the password key's value, to the hash of the current value

    new_customer = Customers(**data) #Creating customer object
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

#Read customers
@customers_bp.route('', methods=['GET']) #Endpoint to get customer information
@cache.cached(timeout=60)
def read_customers():
    customers = db.session.query(customers).all()
    return customers_schema.jsonify(customers), 200

#Read Individual customer - Using a Dynamic Endpoint
@customers_bp.route('<int:customer_id>', methods=['GET'])
def read_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    return customer_schema.jsonify(customer), 200

#Delete a customer
@customers_bp.route('', methods=['DELETE'])
@token_required
def delete_customer(customer_id):
    customer = db.session.get(Customers, customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted customer {customer_id}"}), 200

#Update a customer
@customers_bp.route('', methods=['PUT'])
@token_required
def update_customer(customer_id):
    customer = db.session.get(Customers, customer_id) #Query for our customer to update

    if not customer: #Checking if I got a customer
        return jsonify({"message": "customer not found"}), 404  #if not return error message
    
    try:
        customer_data = customer_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    customer_data['password'] = generate_password_hash(customer_data['password']) #resetting the password key's value, to the hash of the current value
    
    for key, value in customer_data.items(): #Looping over attributes and values from customer data dictionary
        setattr(customer, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return customer_schema.jsonify(customer), 200