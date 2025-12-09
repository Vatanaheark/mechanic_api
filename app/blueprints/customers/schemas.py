from app.extensions import ma
from app.models import Customers

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers #Creates a schema that validates the data as defined by our customers Model

customer_schema = CustomerSchema() 
customers_schema = CustomerSchema(many=True) #Allows this schema to translate a list of customer objects all at once
login_schema = CustomerSchema(exclude=['name'])