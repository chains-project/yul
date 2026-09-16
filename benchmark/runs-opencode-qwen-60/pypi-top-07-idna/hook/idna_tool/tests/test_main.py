"""IDNA encoding and decoding tests."""
import pytest
import idna
from idna_tool.main import encode_domain, decode_domain


class TestEncodeDomain:
    """Tests for IDNA encoding."""

    def test_ascii_domain(self):
        """Test encoding an ASCII domain."""
        result = encode_domain("example.com")
        assert result == "example.com"

    def test_german_umlaut(self):
        """Test encoding a domain with German umlaut."""
        result = encode_domain("münchen.de")
        assert result == "xn--mnchen-3ya.de"

    def test_cyrillic_domain(self):
        """Test encoding a Cyrillic domain."""
        result = encode_domain("пример.рф")
        assert result == "xn--e1afmkfd.xn--p1ai"

    def test_chinese_domain(self):
        """Test encoding a Chinese domain."""
        result = encode_domain("中文.cn")
        assert result == "xn--fiq228c.cn"

    def test_arabic_domain(self):
        """Test encoding an Arabic domain."""
        result = encode_domain("مثال.مصر")
        assert "xn--" in result.lower()

    def test_emoji_domain_fails(self):
        """Test that emoji domains raise an error."""
        with pytest.raises(idna.IDNAError):
            encode_domain("🇺🇸.com")

    def test_subdomain(self):
        """Test encoding a domain with subdomain."""
        result = encode_domain("münchen.example.com")
        assert result == "xn--mnchen-3ya.example.com"

    def test_tld_preserved(self):
        """Test that TLD is preserved during encoding."""
        result = encode_domain("test.münchen.de")
        assert ".de" in result


class TestDecodeDomain:
    """Tests for IDNA decoding."""

    def test_ascii_domain(self):
        """Test decoding an ASCII domain."""
        result = decode_domain("example.com")
        assert result == "example.com"

    def test_punycode_decode(self):
        """Test decoding a punycode domain."""
        result = decode_domain("xn--mnchen-3ya.de")
        assert result == "münchen.de"

    def test_cyrillic_decode(self):
        """Test decoding a Cyrillic punycode domain."""
        result = decode_domain("xn--e1afmkfd.xn--p1ai")
        assert result == "пример.рф"

    def test_chinese_decode(self):
        """Test decoding a Chinese punycode domain."""
        result = decode_domain("xn--fiq228c.cn")
        assert result == "中文.cn"

    def test_subdomain_decode(self):
        """Test decoding a domain with subdomain."""
        result = decode_domain("xn--mnchen-3ya.example.com")
        assert result == "münchen.example.com"

    def test_roundtrip(self):
        """Test encode-decode roundtrip."""
        original = "münchen.de"
        encoded = encode_domain(original)
        decoded = decode_domain(encoded)
        assert decoded == original


class TestIdnaModule:
    """Tests for raw idna module behavior."""

    def test_idna_version(self):
        """Test that idna package is available."""
        assert hasattr(idna, '__version__')

    def test_encode_method_exists(self):
        """Test that idna.encode exists."""
        assert hasattr(idna, 'encode')

    def test_decode_method_exists(self):
        """Test that idna.decode exists."""
        assert hasattr(idna, 'decode')

    def test_uts46_support(self):
        """Test that UTS#46 mapping is supported."""
        result = idna.encode("example.com", uts46=True)
        assert b"example.com" in result


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_domain(self):
        """Test handling of invalid domain."""
        with pytest.raises(idna.IDNAError):
            encode_domain("invalid..domain.com")

    def test_empty_domain(self):
        """Test handling of empty domain."""
        with pytest.raises(idna.IDNAError):
            encode_domain("")

    def test_overly_long_label(self):
        """Test handling of labels that are too long."""
        with pytest.raises(idna.IDNAError):
            encode_domain("a" * 64 + ".com")

    def test_invalid_unicode(self):
        """Test handling of invalid unicode."""
        with pytest.raises(idna.IDNAError):
            encode_domain("test\x00.com")


class TestCommandLine:
    """Tests for command-line interface."""

    def test_encode_via_main(self, monkeypatch):
        """Test encoding via main function."""
        import sys
        from io import StringIO

        monkeypatch.setattr(sys, 'argv', ['idna-tool', 'münchen.de'])
        
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            main()
            output = captured.getvalue()
            assert "xn--mnchen-3ya.de" in output
        finally:
            sys.stdout = old_stdout

    def test_decode_via_main(self, monkeypatch):
        """Test decoding via main function."""
        import sys
        from io import StringIO

        monkeypatch.setattr(sys, 'argv', ['idna-tool', '--decode', 'xn--mnchen-3ya.de'])
        
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            main()
            output = captured.getvalue()
            assert "münchen.de" in output
        finally:
            sys.stdout = old_stdout


def main():
    """CLI entry point for testing."""
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument("domain")
    parser.add_argument("--decode", "-d", action="store_true")
    args = parser.parse_args()

    try:
        if args.decode:
            result = decode_domain(args.domain)
            print(f"Decoded: {result}")
        else:
            result = encode_domain(args.domain)
            print(f"Encoded: {result}")
    except idna.IDNAError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)