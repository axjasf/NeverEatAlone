"""Domain models for contact information templates."""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, UTC
from uuid import UUID
from copy import deepcopy
from pydantic import BaseModel, Field, field_validator
import re


class FieldDefinition(BaseModel):
    """Definition of a single field in a template."""

    name: str
    type: str  # string, date, phone, email
    description: str
    display_format: Optional[str] = None
    reminder_template: Optional[str] = None
    validators: List[str] = Field(default_factory=list)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate field type is one of the allowed values."""
        allowed_types = {"string", "date", "phone", "email"}
        if v not in allowed_types:
            raise ValueError(f"Field type must be one of: {allowed_types}")
        return v


class CategoryDefinition(BaseModel):
    """Definition of a category containing fields."""

    name: str
    description: str
    fields: Dict[str, FieldDefinition]

    @field_validator("fields")
    @classmethod
    def validate_field_names(
        cls, v: Dict[str, FieldDefinition]
    ) -> Dict[str, FieldDefinition]:
        """Ensure field names match their dictionary keys."""
        for key, field in v.items():
            if key != field.name:
                raise ValueError(f"Field name {field.name} does not match key {key}")
        return v


class Template(BaseModel):
    """Template for contact sub_information validation."""

    id: UUID
    categories: Dict[str, CategoryDefinition]
    version: int
    created_at: datetime
    updated_at: datetime
    removed_fields: Dict[str, Set[str]] = Field(default_factory=lambda: {})

    @field_validator("categories")
    @classmethod
    def validate_category_names(
        cls, v: Dict[str, CategoryDefinition]
    ) -> Dict[str, CategoryDefinition]:
        """Ensure category names match their dictionary keys."""
        for key, category in v.items():
            if key != category.name:
                raise ValueError(
                    f"Category name {category.name} does not match key {key}"
                )
        return v

    def evolve(
        self,
        new_fields: Optional[Dict[str, Dict[str, FieldDefinition]]] = None,
        removed_fields: Optional[Dict[str, List[str]]] = None,
        changed_fields: Optional[Dict[str, Dict[str, FieldDefinition]]] = None,
    ) -> "Template":
        """Create a new version of the template with evolved fields.

        Args:
            new_fields: New fields to add, by category
            removed_fields: Fields to remove, by category
            changed_fields: Fields to change, by category

        Returns:
            A new Template instance with the evolved fields and incremented version
        """
        # Create a deep copy of the current template
        new_categories = deepcopy(self.categories)
        new_removed = deepcopy(self.removed_fields)

        # Add new fields
        if new_fields:
            for category_name, fields in new_fields.items():
                if category_name not in new_categories:
                    raise ValueError(f"Unknown category: {category_name}")
                new_categories[category_name].fields.update(fields)

        # Remove fields
        if removed_fields:
            for category_name, field_names in removed_fields.items():
                if category_name not in new_categories:
                    raise ValueError(f"Unknown category: {category_name}")
                # Track removed fields for historical data validation
                if category_name not in new_removed:
                    new_removed[category_name] = set()
                new_removed[category_name].update(field_names)
                # Remove fields from template
                for field_name in field_names:
                    if field_name in new_categories[category_name].fields:
                        del new_categories[category_name].fields[field_name]

        # Change fields
        if changed_fields:
            for category_name, fields in changed_fields.items():
                if category_name not in new_categories:
                    raise ValueError(f"Unknown category: {category_name}")
                for field_name, new_field in fields.items():
                    if field_name not in new_categories[category_name].fields:
                        raise ValueError(
                            f"Unknown field {field_name} in category {category_name}"
                        )
                    new_categories[category_name].fields[field_name] = new_field

        # Create a new version with the same ID
        now = datetime.now(UTC)
        return Template(
            id=self.id,  # Keep the same ID for all versions
            categories=new_categories,
            version=self.version + 1,
            created_at=now,  # New version gets current timestamp
            updated_at=now,
            removed_fields=new_removed,
        )

    def validate_data(self, data: Dict[str, Dict[str, Any]]) -> bool:
        """Validate sub_information against the template.

        Args:
            data: The sub_information dictionary to validate

        Returns:
            bool: True if validation passes

        Raises:
            ValueError: If validation fails, with field name and reason in message
        """
        for category_name, category_data in data.items():
            self._validate_category(category_name, category_data)
        return True

    def _validate_category(self, category_name: str, category_data: Dict[str, Any]) -> None:
        """Validate a single category of data.

        Args:
            category_name: Name of the category
            category_data: Data for the category

        Raises:
            ValueError: If validation fails
        """
        if category_name not in self.categories:
            raise ValueError(f"Unknown category: {category_name}")

        category = self.categories[category_name]
        for field_name, field_value in category_data.items():
            self._validate_field(category_name, category, field_name, field_value)

    def _validate_field(
        self,
        category_name: str,
        category: CategoryDefinition,
        field_name: str,
        field_value: Any
    ) -> None:
        """Validate a single field value.

        Args:
            category_name: Name of the category
            category: Category definition
            field_name: Name of the field
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        # Skip validation for removed fields
        if self._is_removed_field(category_name, field_name):
            return

        if field_name not in category.fields:
            raise ValueError(
                f"Unknown field '{field_name}' in category '{category_name}'"
            )

        field = category.fields[field_name]
        self._validate_field_type(field_name, field_value)
        self._validate_field_format(field_name, field, field_value)

    def _is_removed_field(self, category_name: str, field_name: str) -> bool:
        """Check if a field has been removed.

        Args:
            category_name: Name of the category
            field_name: Name of the field

        Returns:
            bool: True if the field has been removed
        """
        return (
            category_name in self.removed_fields
            and field_name in self.removed_fields[category_name]
        )

    def _validate_field_type(self, field_name: str, field_value: Any) -> None:
        """Validate that a field value is a string.

        Args:
            field_name: Name of the field
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        if not isinstance(field_value, str):
            raise ValueError(f"Field '{field_name}' must be a string")

    def _validate_field_format(self, field_name: str, field: FieldDefinition, field_value: str) -> None:
        """Validate the format of a field value based on its type.

        Args:
            field_name: Name of the field
            field: Field definition
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        if field.type == "date":
            self._validate_date_format(field_name, field_value)
        elif field.type == "phone":
            self._validate_phone_format(field_name, field_value)
        elif field.type == "email":
            self._validate_email_format(field_name, field_value)

    def _validate_date_format(self, field_name: str, field_value: str) -> None:
        """Validate a date field.

        Args:
            field_name: Name of the field
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        try:
            datetime.fromisoformat(field_value)
        except ValueError:
            raise ValueError(
                f"Field '{field_name}' must be a valid ISO date string (YYYY-MM-DD)"
            )

    def _validate_phone_format(self, field_name: str, field_value: str) -> None:
        """Validate a phone number field.

        Args:
            field_name: Name of the field
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_phone_number(field_value):
            raise ValueError(
                f"Field '{field_name}' must be a valid phone number (+X XXX-XXX-XXXX)"
            )

    def _validate_email_format(self, field_name: str, field_value: str) -> None:
        """Validate an email field.

        Args:
            field_name: Name of the field
            field_value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        if not self._validate_email(field_value):
            raise ValueError(
                f"Field '{field_name}' must be a valid email address"
            )

    def _validate_phone_number(self, value: str) -> bool:
        """Validate phone number format (+X XXX-XXX-XXXX)."""
        pattern = r"^\+\d{1,3}[\s-]\d{3}[\s-]\d{3}[\s-]\d{4}$"
        return bool(re.match(pattern, value))

    def _validate_email(self, value: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, value))

    def get_filled_fields(
        self, data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Get only the filled fields from sub_information.

        Args:
            data: The sub_information dictionary

        Returns:
            Dict containing only non-empty fields
        """
        filled: Dict[str, Dict[str, Any]] = {}

        for category_name, category_data in data.items():
            if category_name in self.categories:
                category_filled = {
                    k: v
                    for k, v in category_data.items()
                    if k in self.categories[category_name].fields
                    and v is not None
                    and (not isinstance(v, str) or v.strip())
                }
                if category_filled:
                    filled[category_name] = category_filled

        return filled
