"""Customer business logic service."""
from typing import List, Optional
from database.models import Customer
from database.repositories import CustomerRepository


class CustomerService:
    @staticmethod
    def get_or_create(customer_id: str, name: str, email: str, product: str, plan: str, environment: str) -> Customer:
        cust = CustomerRepository.get_by_id(customer_id)
        if not cust:
            cust = CustomerRepository.create(
                customer_id=customer_id,
                name=name,
                email=email,
                product=product,
                plan=plan,
                environment=environment,
            )
        return cust

    @staticmethod
    def list_all() -> List[Customer]:
        return CustomerRepository.list_all()

    @staticmethod
    def get_by_id(customer_id: str) -> Optional[Customer]:
        return CustomerRepository.get_by_id(customer_id)
