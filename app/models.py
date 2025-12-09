from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, String, Table, Column, ForeignKey, DateTime, Float, Integer

# create  base class for our models
class Base(DeclarativeBase):
    pass

#Instatiate your SQLAlchemy database:
db = SQLAlchemy(model_class = Base)

ticket_mechanics = db.Table(
    'ticket_mechanics',
    Base.metadata,
    db.Column('ticket_id', ForeignKey('tickets.id')),
    db.Column('mechanic_id', ForeignKey('mechanics.id'))
)


class Customers(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)

    #One to Many relationship from customer to Mechanics
    tickets: Mapped[list['Tickets']] = relationship('Tickets', back_populates='customer')
  
  
class Tickets(Base):
    __tablename__ = 'tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_date: Mapped[date] = mapped_column(Date, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)

    #Relationships
    customer: Mapped['Customers'] = relationship('Customers', back_populates='tickets')
    mechanics: Mapped[list['Mechanics']] = relationship("Mechanics", secondary=ticket_mechanics, back_populates='tickets') #Many to Many relationship going through the ticket_mechanics table
 

class Mechanics(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(120), nullable=False)
    salary: Mapped[str] = mapped_column(String(500), nullable=True)

    #Relationship
    tickets: Mapped[list['Tickets']] = relationship('Tickets', secondary=ticket_mechanics, back_populates='mechanics')