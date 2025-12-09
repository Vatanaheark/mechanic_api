from app.extensions import ma
from app.models import Mechanics

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics #Creates a schema that validates the data as defined by our Loans Model

mechanic_schema = MechanicSchema() 
mechanics_schema = MechanicSchema(many=True)