"""
app/repositories/customer_repository.py
========================================
Data-access layer for the Customer entity using the Repository pattern.

This module is the ONLY place in the application that directly talks to the
Customer table.  All SQL construction, transaction management, and raw
database error handling lives here.  The service layer consumes this class
through its public interface and never touches ``db.session`` directly.
"""

from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.customer import Customer
from app.utils.exceptions import (
    CustomerNotFoundError,
    DuplicateCustomerEmailError,
    RepositoryError,
)

logger = logging.getLogger(__name__)


class CustomerRepository:
    """
    Encapsulates all CRUD and query operations for the Customer model.

    Methods raise domain-level exceptions (never raw SQLAlchemy errors) so
    that the service layer operates exclusively in terms of domain language.
    """

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(self, data: dict) -> Customer:
        """
        Persist a new Customer record to the database.

        Parameters
        ----------
        data : dict
            Validated customer fields.  Must contain at minimum ``name``
            and ``email``.

        Returns
        -------
        Customer
            The newly created, committed Customer instance.

        Raises
        ------
        DuplicateCustomerEmailError
            If a customer with the same email already exists.
        RepositoryError
            On any other unexpected database failure.
        """
        logger.debug("CustomerRepository.create | email=%s", data.get("email"))
        customer = Customer(
            name=data["name"],
            email=data["email"].lower().strip(),
            phone=data.get("phone"),
            company=data.get("company"),
            address=data.get("address"),
            status=data.get("status", "active"),
            source=data.get("source"),
        )
        try:
            db.session.add(customer)
            db.session.commit()
            db.session.refresh(customer)
            logger.info("Customer created | id=%d email=%s", customer.id, customer.email)
            return customer
        except IntegrityError as exc:
            db.session.rollback()
            if "UNIQUE" in str(exc.orig).upper() or "unique" in str(exc.orig).lower():
                logger.warning(
                    "Duplicate customer email attempt | email=%s", data.get("email")
                )
                raise DuplicateCustomerEmailError(data["email"]) from exc
            raise RepositoryError("create_customer", exc) from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error on customer create: %s", exc)
            raise RepositoryError("create_customer", exc) from exc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get_by_id(self, customer_id: int) -> Customer:
        """
        Retrieve a Customer by primary key.

        Raises
        ------
        CustomerNotFoundError
            If no Customer with ``customer_id`` exists.
        RepositoryError
            On database failure.
        """
        logger.debug("CustomerRepository.get_by_id | id=%d", customer_id)
        try:
            customer = db.session.get(Customer, customer_id)
        except SQLAlchemyError as exc:
            logger.error("DB error fetching customer id=%d: %s", customer_id, exc)
            raise RepositoryError("get_customer_by_id", exc) from exc

        if customer is None:
            raise CustomerNotFoundError(customer_id)
        return customer

    def get_by_email(self, email: str) -> Optional[Customer]:
        """
        Look up a Customer by their unique email address.

        Returns ``None`` if no match is found (non-raising – lets the caller
        decide whether absence is an error).

        Raises
        ------
        RepositoryError
            On database failure.
        """
        normalised = email.lower().strip()
        logger.debug("CustomerRepository.get_by_email | email=%s", normalised)
        try:
            return Customer.query.filter_by(email=normalised).first()
        except SQLAlchemyError as exc:
            logger.error("DB error looking up customer email=%s: %s", normalised, exc)
            raise RepositoryError("get_customer_by_email", exc) from exc

    def get_all(
        self,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """
        Return a paginated list of Customers.

        Parameters
        ----------
        status : str | None
            Optional filter on the customer status column.
        page : int
            1-based page number.
        per_page : int
            Maximum records per page.

        Returns
        -------
        dict
            Keys: ``items`` (list[Customer]), ``total``, ``page``,
            ``per_page``, ``pages``.
        """
        logger.debug(
            "CustomerRepository.get_all | status=%s page=%d per_page=%d",
            status, page, per_page,
        )
        try:
            query = Customer.query.order_by(Customer.created_at.desc())
            if status:
                query = query.filter_by(status=status)
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            logger.error("DB error listing customers: %s", exc)
            raise RepositoryError("list_customers", exc) from exc

    def search(self, query_str: str, page: int = 1, per_page: int = 20) -> dict:
        """
        Full-text-style search across ``name``, ``email``, and ``company``.

        Uses SQLite ``LIKE`` with leading wildcard – adequate for a Mini CRM.

        Returns
        -------
        dict
            Same shape as ``get_all``.
        """
        term = f"%{query_str.strip()}%"
        logger.debug("CustomerRepository.search | term=%r", term)
        try:
            query = (
                Customer.query
                .filter(
                    db.or_(
                        Customer.name.ilike(term),
                        Customer.email.ilike(term),
                        Customer.company.ilike(term),
                    )
                )
                .order_by(Customer.name.asc())
            )
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            return {
                "items": pagination.items,
                "total": pagination.total,
                "page": pagination.page,
                "per_page": pagination.per_page,
                "pages": pagination.pages,
            }
        except SQLAlchemyError as exc:
            logger.error("DB error searching customers: %s", exc)
            raise RepositoryError("search_customers", exc) from exc

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(self, customer_id: int, data: dict) -> Customer:
        """
        Apply a partial update to an existing Customer record.

        Only the fields present in ``data`` are modified; absent fields are
        left unchanged (PATCH semantics).

        Returns
        -------
        Customer
            The updated, committed Customer instance.

        Raises
        ------
        CustomerNotFoundError
            If no Customer with ``customer_id`` exists.
        DuplicateCustomerEmailError
            If the new email collides with another customer.
        RepositoryError
            On any unexpected database failure.
        """
        logger.debug("CustomerRepository.update | id=%d fields=%s", customer_id, list(data.keys()))
        customer = self.get_by_id(customer_id)  # raises CustomerNotFoundError if absent

        updatable_fields = ("name", "phone", "company", "address", "status", "source")
        for field in updatable_fields:
            if field in data:
                setattr(customer, field, data[field])

        if "email" in data:
            customer.email = data["email"].lower().strip()

        try:
            db.session.commit()
            db.session.refresh(customer)
            logger.info("Customer updated | id=%d", customer.id)
            return customer
        except IntegrityError as exc:
            db.session.rollback()
            if "UNIQUE" in str(exc.orig).upper() or "unique" in str(exc.orig).lower():
                raise DuplicateCustomerEmailError(data.get("email", "")) from exc
            raise RepositoryError("update_customer", exc) from exc
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error updating customer id=%d: %s", customer_id, exc)
            raise RepositoryError("update_customer", exc) from exc

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, customer_id: int) -> None:
        """
        Hard-delete a Customer record and all its cascade-linked records.

        Raises
        ------
        CustomerNotFoundError
            If no Customer with ``customer_id`` exists.
        RepositoryError
            On database failure.
        """
        logger.debug("CustomerRepository.delete | id=%d", customer_id)
        customer = self.get_by_id(customer_id)  # raises CustomerNotFoundError if absent
        try:
            db.session.delete(customer)
            db.session.commit()
            logger.info("Customer deleted | id=%d", customer_id)
        except SQLAlchemyError as exc:
            db.session.rollback()
            logger.error("DB error deleting customer id=%d: %s", customer_id, exc)
            raise RepositoryError("delete_customer", exc) from exc

    # ------------------------------------------------------------------
    # Existence check (used by service layer)
    # ------------------------------------------------------------------

    def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """
        Return ``True`` if any Customer row has the given email.

        Parameters
        ----------
        email : str
            Email address to check (normalised internally).
        exclude_id : int | None
            Exclude this Customer ID from the check (useful during updates).
        """
        normalised = email.lower().strip()
        try:
            query = Customer.query.filter_by(email=normalised)
            if exclude_id is not None:
                query = query.filter(Customer.id != exclude_id)
            return db.session.query(query.exists()).scalar()
        except SQLAlchemyError as exc:
            raise RepositoryError("check_email_exists", exc) from exc
