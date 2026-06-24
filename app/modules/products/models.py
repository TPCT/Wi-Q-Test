from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_id: int = Field(exclude=True)
    name: str


class ProductRenameRequest(BaseModel):
    name: str = Field(min_length=1)
