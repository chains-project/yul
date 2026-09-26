import sys

import idna


def encode(domain: str) -> str:
    return idna.encode(domain).decode("ascii")


def decode(domain: str) -> str:
    return idna.decode(domain)


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ("encode", "decode"):
        print(f"usage: {sys.argv[0]} <encode|decode> <domain>", file=sys.stderr)
        raise SystemExit(1)

    command, domain = sys.argv[1], sys.argv[2]
    result = encode(domain) if command == "encode" else decode(domain)
    print(result)


if __name__ == "__main__":
    main()
