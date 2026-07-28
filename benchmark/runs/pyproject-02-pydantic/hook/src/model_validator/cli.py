import argparse
import json
import sys

from pydantic import ValidationError

from .models import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate JSON records against the User model")
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="JSON file to validate (defaults to stdin)",
    )
    args = parser.parse_args()

    data = json.load(args.file)
    records = data if isinstance(data, list) else [data]

    exit_code = 0
    for i, record in enumerate(records):
        try:
            user = User.model_validate(record)
        except ValidationError as e:
            exit_code = 1
            print(f"record {i}: invalid", file=sys.stderr)
            print(e, file=sys.stderr)
        else:
            print(user.model_dump_json())

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
