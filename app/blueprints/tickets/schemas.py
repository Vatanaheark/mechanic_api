from app.extensions import ma
from app.models import Tickets

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tickets #Creates a schema that validates the data as defined by our tickets Model
        include_fk = True

ticket_schema = TicketSchema() 
tickets_schema = TicketSchema(many=True) 