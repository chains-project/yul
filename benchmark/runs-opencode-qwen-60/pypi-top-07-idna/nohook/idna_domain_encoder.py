import idna


def encode_domain(domain: str) -> str:
    """Encode an internationalized domain name to its ASCII (Punycode) form."""
    try:
        encoded = idna.encode(domain)
        return encoded.decode("ascii")
    except idna.core.IDNAError as e:
        raise ValueError(f"Failed to encode domain '{domain}': {e}")


def decode_domain(domain: str) -> str:
    """Decode an ASCII (Punycoded) domain name to its Unicode form."""
    try:
        decoded = idna.decode(domain)
        return decoded
    except idna.core.IDNAError as e:
        raise ValueError(f"Failed to decode domain '{domain}': {e}")


def main() -> None:
    """Demo encoding and decoding of internationalized domain names."""
    test_domains = [
        "münchen.de",
        "中国.cn",
        "xn--mnchen-3ya.de",
        "xn--fiqs8s.cn",
        "café.com",
        "日本.jp",
    ]

    print("IDNA Domain Encoding/Decoding Demo")
    print("=" * 50)

    for domain in test_domains:
        try:
            encoded = encode_domain(domain)
            print(f"  Encode: {domain}  ->  {encoded}")
        except ValueError as e:
            # Likely already an ASCII/Punycode domain
            try:
                decoded = decode_domain(domain)
                print(f"  Decode: {domain}  ->  {decoded}")
            except ValueError as e2:
                print(f"  Error: {e2}")

    print("=" * 50)
    print(f"idna library version: {idna.__version__}")


if __name__ == "__main__":
    main()