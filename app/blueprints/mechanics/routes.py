from app.blueprints.mechanics import mechanics_bp
from .schemas import mechanics_schema, mechanics_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import limiter, cache
from app.models import Mechanics, db
from sqlalchemy import select

#CREATE MECHANIC ROUTE
@mechanics_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
def create_mechanic():
    try:
        data = mechanics_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    

    new_mechanic = Mechanics(**data) #Creating Mechanic object
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanics_schema.jsonify(new_mechanic), 201

#Read Mechanics
@mechanics_bp.route('', methods=['GET']) #Endpoint to get mechanic information
@cache.cached(timeout=30) 
def read_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanics)
        mechanics = db.paginate(query, page=page, per_page=per_page) # Handles out pagination
        print("Page and per page")
        print(jsonify(mechanics))
        return mechanics_schema.jsonify(mechanics), 200
    except: # Defaulting to our regular if they don't send a page or page number  
        mechanics = db.session.query(mechanics).all()
        print("Default")
        return mechanics_schema.jsonify(mechanics), 200

#Read Individual Mechanic - Using a Dynamic Endpoint
@mechanics_bp.route('<int:mechanic_id>', methods=['GET'])
def read_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    return mechanics_schema.jsonify(mechanic), 200

#Delete a mechanic
@mechanics_bp.route('<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted {mechanic_id}"}), 200

#Update a Mechanics
@mechanics_bp.route('<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    mechanic = db.session.get(Mechanics, mechanic_id) #Query for our mechanic to update

    if not mechanic: #Checking if I got a mechanic
        return jsonify({"message": "mechanic not found"}), 404  #if not return error message
    
    try:
        mechanic_data = mechanics_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in mechanic_data.items(): #Looping over attributes and values from mechanic data dictionary
        setattr(mechanic, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return mechanics_schema.jsonify(mechanic), 200

# Get Popular Mechanics
# @mechanics_bp.route('/popularity', methods=['GET'])
# def get_popular_mechanics():
    
#     mechanics = db.session.query(mechanics).all() # Grabbing all mechanics
    
#     # Sort mechanics list base off of how many loans they've been apart of
#     mechanics.sort(key= lambda mechanic: len(mechanic.loans), reverse=True) # Reversing to get the most popular mechanics first
    
#     output = []
#     for mechanic in mechanics[:5]: # For each individual mechanic
#         mechanic_format = {
#             "mechanic": mechanics_schema.dump(mechanic), # translate the mechanic to json
#             "readers": len(mechanic.loans) # add the amount of readers
#         }
#         output.append(mechanic_format) # append this dictionary to an output list
        
#     return jsonify(output), 200 #jsonify the output list

# Search for a mechanic based on the title or author
@mechanics_bp.route('/search', methods=['GET'])
def search_mechanic():
    phone = request.args.get('phone')  # Accessing the query parameters from the URL
    name = request.args.get('name')  # Accessing the query parameters from the URL
    
    if phone:
        mechanics = db.session.query(Mechanics).where(Mechanics.phone.like(f'%{phone}%')).all()
    elif name:
       mechanics = db.session.query(Mechanics).where(Mechanics.name.like(f'%{name}%')).all()
    
    return mechanics_schema.jsonify(mechanics), 200