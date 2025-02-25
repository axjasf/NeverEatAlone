"""Service layer package.

This package provides the service layer implementation, organizing business logic
and transaction management for the application. The services are organized into
core and supporting services.

Core Services:
- base_service: Foundation for all services
- contact: Contact management with custom fields
- note: Note and interaction management
- statement: Statement sequence management
- tag: Polymorphic tag operations

Supporting Services:
- template: Contact field definitions and versioning
- reminder: Recurrence and timezone-aware reminders
- interaction: Interaction tracking and history
"""

from .base_service import (  # noqa: F401
    ServiceError,
    ValidationError,
    TransactionError,
    NotFoundError,
    BaseService
)
