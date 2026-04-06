"""Base model for all Vchasno data models."""

from pydantic import BaseModel


class VchasnoModel(BaseModel):
    """Base model with standard Vchasno configuration.
    
    Enables:
    - extra="allow" for forward compatibility with API changes
    - populate_by_name=True for both snake_case and camelCase field names
    """

    model_config = {"extra": "allow", "populate_by_name": True}
