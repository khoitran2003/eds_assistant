from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.customers import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate


def get(*, session: Session, id: str) -> Optional[Customer]:
    """
    Get a customer by ID.
    """
    return session.get(Customer, id)


def get_multi(session: Session, *, skip: int = 0, limit: int = 100) -> List[Customer]:
    """
    Get a list of customers.
    """
    statement = select(Customer).offset(skip).limit(limit)
    customers = session.exec(statement).all()
    return list(customers)


def create(*, session: Session, customer_in: CustomerCreate) -> Customer:
    """
    Create a new customer.
    """
    db_obj = Customer.model_validate(customer_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update(
    *, session: Session, db_customer: Customer, customer_in: CustomerUpdate
) -> Customer:
    """
    Update a customer.
    """
    update_data = customer_in.model_dump(exclude_unset=True)
    db_customer.sqlmodel_update(update_data)
    session.add(db_customer)
    session.commit()
    session.refresh(db_customer)
    return db_customer

