import pytest
from pydantic import ValidationError

from model_validator.models import User


def test_valid_user():
    user = User(id=1, name="Ada Lovelace", email="ada@example.com", age=36)
    assert user.age == 36


def test_invalid_email():
    with pytest.raises(ValidationError):
        User(id=1, name="Ada Lovelace", email="not-an-email", age=36)


def test_invalid_age():
    with pytest.raises(ValidationError):
        User(id=1, name="Ada Lovelace", email="ada@example.com", age=200)
