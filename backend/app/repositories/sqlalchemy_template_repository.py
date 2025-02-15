"""SQLAlchemy implementation of template repository."""

from typing import List, Optional, Dict, Set, TypedDict
from uuid import UUID
from datetime import UTC
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.domain.template_model import Template, CategoryDefinition, FieldDefinition
from ..models.orm.template_orm import TemplateVersionORM


class FieldDict(TypedDict):
    name: str
    type: str
    description: str
    display_format: Optional[str]
    reminder_template: Optional[str]
    validators: List[str]

class CategoryDict(TypedDict):
    name: str
    description: str
    fields: Dict[str, FieldDict]


class SQLAlchemyTemplateRepository:
    """SQLAlchemy implementation of template repository."""

    def __init__(self, session: Session) -> None:
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy database session
        """
        self._session = session

    def _to_json_dict(self, template: Template) -> Dict[str, CategoryDict]:
        """Convert template to JSON-serializable dictionary.

        Args:
            template: Template to convert

        Returns:
            Dictionary representation of the template
        """
        categories_dict: Dict[str, CategoryDict] = {}
        for category_name, category in template.categories.items():
            fields_dict: Dict[str, FieldDict] = {}
            for field_name, field in category.fields.items():
                fields_dict[field_name] = {
                    "name": field.name,
                    "type": field.type,
                    "description": field.description,
                    "display_format": field.display_format,
                    "reminder_template": field.reminder_template,
                    "validators": field.validators,
                }
            categories_dict[category_name] = {
                "name": category.name,
                "description": category.description,
                "fields": fields_dict,
            }
        return categories_dict

    def _from_json_dict(self, data: Dict[str, CategoryDict]) -> Dict[str, CategoryDefinition]:
        """Convert JSON dictionary back to domain objects.

        Args:
            data: Dictionary from database

        Returns:
            Dictionary of CategoryDefinition objects
        """
        categories: Dict[str, CategoryDefinition] = {}
        for category_name, category_data in data.items():
            fields: Dict[str, FieldDefinition] = {}
            for field_name, field_data in category_data["fields"].items():
                fields[field_name] = FieldDefinition(
                    name=field_data["name"],
                    type=field_data["type"],
                    description=field_data["description"],
                    display_format=field_data.get("display_format"),
                    reminder_template=field_data.get("reminder_template"),
                    validators=field_data.get("validators", []),
                )
            categories[category_name] = CategoryDefinition(
                name=category_data["name"],
                description=category_data["description"],
                fields=fields,
            )
        return categories

    def _to_json_removed_fields(
        self, removed_fields: Dict[str, Set[str]]
    ) -> Dict[str, list[str]]:
        """Convert removed_fields to JSON-serializable dictionary.

        Args:
            removed_fields: Dictionary of removed fields by category

        Returns:
            Dictionary with sets converted to lists for JSON serialization
        """
        return {category: list(fields) for category, fields in removed_fields.items()}

    def _from_json_removed_fields(
        self, data: Dict[str, list[str]]
    ) -> Dict[str, Set[str]]:
        """Convert JSON dictionary back to removed_fields format.

        Args:
            data: Dictionary from database

        Returns:
            Dictionary with lists converted to sets
        """
        return {category: set(fields) for category, fields in data.items()}

    def save(self, template: Template) -> None:
        """Save a template.

        Args:
            template: The template to save
        """
        # Convert domain model to ORM
        template_orm = TemplateVersionORM(
            id=template.id,
            version=template.version,
            categories=self._to_json_dict(template),
            removed_fields=self._to_json_removed_fields(template.removed_fields),
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

        # Always add as a new version
        self._session.add(template_orm)
        self._session.flush()

    def get_by_id(self, template_id: UUID) -> Optional[Template]:
        """Get latest version of a template by its ID.

        Args:
            template_id: UUID of the template to find

        Returns:
            Template if found, None if not found
        """
        # Get the latest version
        stmt = (
            select(TemplateVersionORM)
            .where(TemplateVersionORM.id == template_id)
            .order_by(TemplateVersionORM.version.desc())
            .limit(1)
        )
        template_orm = self._session.execute(stmt).scalar_one_or_none()

        if template_orm is None:
            return None

        # Convert to domain model
        return Template(
            id=template_orm.id,
            version=template_orm.version,
            categories=self._from_json_dict(template_orm.categories),
            created_at=template_orm.created_at.replace(tzinfo=UTC),
            updated_at=template_orm.updated_at.replace(tzinfo=UTC),
            removed_fields=self._from_json_removed_fields(template_orm.removed_fields),
        )

    def get_version(self, template_id: UUID, version: int) -> Optional[Template]:
        """Get a specific version of a template.

        Args:
            template_id: UUID of the template
            version: Version number to retrieve

        Returns:
            Template if found, None if not found
        """
        # Get the specific version
        stmt = select(TemplateVersionORM).where(
            TemplateVersionORM.id == template_id, TemplateVersionORM.version == version
        )
        template_orm = self._session.execute(stmt).scalar_one_or_none()

        if template_orm is None:
            return None

        # Convert to domain model
        return Template(
            id=template_orm.id,
            version=template_orm.version,
            categories=self._from_json_dict(template_orm.categories),
            created_at=template_orm.created_at.replace(tzinfo=UTC),
            updated_at=template_orm.updated_at.replace(tzinfo=UTC),
            removed_fields=self._from_json_removed_fields(template_orm.removed_fields),
        )

    def get_versions(self, template_id: UUID) -> List[Template]:
        """Get all versions of a template.

        Args:
            template_id: UUID of the template

        Returns:
            List of all versions of the template, ordered by version number
        """
        # Get all versions ordered by version number
        stmt = (
            select(TemplateVersionORM)
            .where(TemplateVersionORM.id == template_id)
            .order_by(TemplateVersionORM.version)
        )
        template_orms = self._session.execute(stmt).scalars().all()

        # Convert to domain models
        templates: List[Template] = []

        for template_orm in template_orms:
            # Convert to domain model
            template = Template(
                id=template_orm.id,
                version=template_orm.version,
                categories=self._from_json_dict(template_orm.categories),
                created_at=template_orm.created_at.replace(tzinfo=UTC),
                updated_at=template_orm.updated_at.replace(tzinfo=UTC),
                removed_fields=self._from_json_removed_fields(
                    template_orm.removed_fields
                ),
            )
            templates.append(template)

        return templates
