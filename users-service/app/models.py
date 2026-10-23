"""User table and the shapes of data the API accepts and returns."""

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=7, max_length=20)
    address: str = Field(min_length=1, max_length=200)


class User(UserBase, table=True):
    """A row in the `user` table."""

    id: int | None = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    """What a client sends to create a user."""


class UserRead(UserBase):
    """What the API sends back."""

    id: int
