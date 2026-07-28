import sys

from pydantic import ValidationError

from model_validator.models import User


def validate(data: dict) -> User:
    return User.model_validate(data)


def main() -> int:
    sample = {"id": 1, "name": "Ada Lovelace", "email": "ada@example.com", "age": 36}
    try:
        user = validate(sample)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(user.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
