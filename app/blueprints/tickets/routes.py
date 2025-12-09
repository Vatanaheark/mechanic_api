from app.blueprints.tickets import tickets_bp
from .schemas import ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Tickets, db, Mechanics
from app.blueprints.mechanics.schemas import mechanics_schema
from app.extensions import limiter, cache

#CREATE TICKET ROUTE
@tickets_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
def create_ticket():
    try:
        data = ticket_schema.ticket(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_ticket = Tickets(**data)
    
    db.session.add(new_ticket)
    db.session.commit()
    return ticket_schema.jsonify(new_ticket), 201

#Add mechanic to ticket
@tickets_bp.route('/<int:ticket_id>/add-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("600 per day", override_defaults=True)
def add_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic not in ticket.mechanics: #checking to see if a relationship already exist between ticket and mechanic
        ticket.mechanics.append(mechanic) #creating a relationship between ticket and mechanic
        db.session.commit()
        return jsonify({
            'message': f'successfully add {mechanic.name} to ticket',
            'ticket': ticket_schema.dump(ticket),  #use dump when the schema is adding just a piece of the return message
            'mechanics': mechanics_schema.dump(ticket.mechanics) #using the mechanics_schema to serialize the list of mechanics related to the ticket
        }), 200
    
    return jsonify("This mechanic is already on the ticket"), 400

#Remove mechanic from ticket
@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("200 per day", override_defaults=True)
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Tickets, ticket_id)
    mechanic = db.session.get(Mechanics, mechanic_id)

    if mechanic in ticket.mechanics: #checking to see if a relationship already exist between ticket and mechanic
        ticket.mechanics.remove(mechanic) #removing the relationship between ticket and mechanic
        db.session.commit()
        return jsonify({
            'message': f'successfully removed {mechanic.name} from ticket',
            'ticket': ticket_schema.dump(ticket),  #use dump when the schema is adding just a piece of the return message
            'mechanics': mechanics_schema.dump(ticket.mechanics) #using the mechanics_schema to serialize the list of mechanics related to the ticket
        }), 200
    
    return jsonify("This mechanic is no on the ticket"), 400

#Read Tickets
@tickets_bp.route('', methods=['GET']) #Endpoint to get ticket information
def read_tickets():
    tickets = db.session.query(tickets).all()
    return tickets_schema.jsonify(tickets), 200

#Read Individual Ticket - Using a Dynamic Endpoint
@tickets_bp.route('<int:ticket_id>', methods=['GET'])
def read_ticket(ticket_id):
    ticket= db.session.get(Tickets, ticket_id)
    return ticket_schema.jsonify(ticket), 200

#Delete a Ticket
@tickets_bp.route('<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted ticket {ticket_id}"}), 200

#Update a Ticket
@tickets_bp.route('<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = db.session.get(Tickets, ticket_id) #Query for our ticket to update

    if not ticket: #Checking if I got a ticket
        return jsonify({"message": "ticket not found"}), 404  #if not return error message
    
    try:
        ticket_data = ticket_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in ticket_data.items(): #Looping over attributes and values from ticket data dictionary
        setattr(ticket, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return ticket_schema.jsonify(ticket), 200