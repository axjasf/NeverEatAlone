from typing import Any, Dict, List, cast, Optional
from datetime import datetime, UTC
from sqlalchemy import Column, String, JSON, DateTime
from .base import BaseModel


class Contact(BaseModel):
    """Contact model for storing contact information.

    This model represents a contact in the system, storing both required and
    optional information about the contact. It supports flexible additional
    information through a JSON field and categorization via hashtags.

    Attributes:
        name (str): Required. The full name of the contact.
        first_name (Optional[str]): Optional. The contact's first name.
        contact_briefing_text (Optional[str]): Optional. Brief notes about
            the contact.
        last_contact (Optional[datetime]): Last contact date in UTC.
        sub_information (Dict[str, Any]): Additional structured information
            stored as JSON. Defaults to empty dict.
        hashtags (List[str]): List of hashtags for categorization. Each tag
            must start with '#'. Defaults to empty list.

    Example:
        >>> contact = Contact(
        ...     name="John Doe",
        ...     first_name="John",
        ...     contact_briefing_text="Met at conference",
        ...     sub_information={"role": "Developer"},
        ...     hashtags=["#tech", "#conference"]
        ... )
    """

    __tablename__ = "contacts"

    _name = Column("name", String, nullable=False)
    _first_name = Column("first_name", String, nullable=True)
    _contact_briefing_text = Column(
        "contact_briefing_text",
        String,
        nullable=True
    )
    _last_contact = Column(
        "last_contact",
        DateTime(timezone=True),
        nullable=True
    )
    _sub_information = Column(
        "sub_information",
        JSON,
        nullable=False,
        default=dict
    )
    _hashtags = Column("hashtags", JSON, nullable=False, default=list)

    @property
    def name(self) -> str:
        """The full name of the contact.

        Returns:
            str: The contact's full name, or empty string if not set.
        """
        val = getattr(self, "_name", None)
        return str(val) if val is not None else ""

    @name.setter
    def name(self, value: str) -> None:
        """Set the contact's full name.

        Args:
            value (str): The full name to set.
        """
        self._name = value

    @property
    def first_name(self) -> Optional[str]:
        """The contact's first name.

        Returns:
            Optional[str]: The contact's first name, or None if not set.
        """
        val = getattr(self, "_first_name", None)
        return str(val) if val is not None else None

    @first_name.setter
    def first_name(self, value: Optional[str]) -> None:
        """Set the contact's first name.

        Args:
            value (Optional[str]): The first name to set, or None to unset.
        """
        self._first_name = value

    @property
    def contact_briefing_text(self) -> Optional[str]:
        """Brief notes about the contact.

        Returns:
            Optional[str]: The briefing text, or None if not set.
        """
        val = getattr(self, "_contact_briefing_text", None)
        return str(val) if val is not None else None

    @contact_briefing_text.setter
    def contact_briefing_text(self, value: Optional[str]) -> None:
        """Set the contact briefing text.

        Args:
            value (Optional[str]): The briefing text to set, or None to unset.
        """
        self._contact_briefing_text = value

    @property
    def last_contact(self) -> Optional[datetime]:
        """The date of last contact with this person.

        Returns:
            Optional[datetime]: The last contact date in UTC,
            or None if not set.
        """
        val = getattr(self, "_last_contact", None)
        if val is not None and val.tzinfo is None:
            val = val.replace(tzinfo=UTC)
        return val

    @last_contact.setter
    def last_contact(self, value: Optional[datetime]) -> None:
        """Set the last contact date.

        Args:
            value (Optional[datetime]): The date to set in UTC,
            or None to unset.
        """
        if value is not None and value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        self._last_contact = value

    @property
    def sub_information(self) -> Dict[str, Any]:
        """Additional structured information about the contact.

        This field can store any JSON-serializable data structure, allowing
        for flexible storage of contact-related information.

        Returns:
            Dict[str, Any]: The stored information, or empty dict if not set.
        """
        val = getattr(self, "_sub_information", {})
        return cast(Dict[str, Any], val)

    @sub_information.setter
    def sub_information(self, value: Dict[str, Any]) -> None:
        """Set additional information about the contact.

        Args:
            value (Dict[str, Any]): The information to store. Must be
                JSON-serializable.

        Raises:
            ValueError: If value is not a dictionary.
        """
        if not isinstance(value, dict):  # type: ignore
            raise ValueError("sub_information must be a dictionary")
        self._sub_information = value

    @property
    def hashtags(self) -> List[str]:
        """List of hashtags associated with the contact.

        These tags can be used for categorization and searching. Each tag
        must start with '#'.

        Returns:
            List[str]: The list of hashtags, or empty list if not set.
        """
        val = getattr(self, "_hashtags", [])
        return cast(List[str], val)

    @hashtags.setter
    def hashtags(self, value: List[str]) -> None:
        """Set the hashtags for the contact.

        Args:
            value (List[str]): List of hashtags. Each tag must start with '#'.

        Raises:
            ValueError: If any tag doesn't start with '#'.
        """
        for tag in value:
            if not tag.startswith("#"):
                raise ValueError(
                    "Each hashtag must be a string starting with #"
                )
        self._hashtags = value
