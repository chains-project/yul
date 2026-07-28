import pytest
from pydantic import ValidationError

from model_validator.models import User


def test_valid_user():
    user = User(name="Ada", email="ada@example.com", age=30)
    assert user.age == 30


def test_invalid_email():
    with pytest.raises(ValidationError):
        User(name="Ada", email="not-an-email", age=30)


def test_invalid_age():
    with pytest.raises(ValidationError):
        User(name="Ada", email="ada@example.com", age=-1)
