use proc_macro2::{Ident, Literal, Punct, Spacing, Span, TokenStream, TokenTree};
use std::fmt;

/// A stable wrapper around `proc_macro2::TokenStream` that provides
/// a more ergonomic API for building and inspecting token streams.
///
/// This type is designed to work both inside and outside procedural macro
/// implementations, providing a consistent interface regardless of context.
#[derive(Debug, Clone)]
pub struct TokenStreamWrapper {
    inner: TokenStream,
}

impl TokenStreamWrapper {
    /// Creates a new empty token stream.
    pub fn new() -> Self {
        Self {
            inner: TokenStream::new(),
        }
    }

    /// Creates a token stream from a vec of token trees.
    pub fn from_vec(trees: Vec<TokenTree>) -> Self {
        Self {
            inner: trees.into_iter().collect(),
        }
    }

    /// Converts this wrapper into the raw `TokenStream`.
    pub fn to_stream(&self) -> TokenStream {
        self.inner.clone()
    }

    /// Appends a token tree to the end of this stream.
    pub fn append<T: Into<TokenTree>>(&mut self, token: T) {
        self.inner.extend(Some(token.into()));
    }

    /// Appends all token trees from another stream.
    pub fn append_stream(&mut self, other: &TokenStreamWrapper) {
        self.inner.extend(other.to_stream());
    }

    /// Prepends a token tree to the beginning of this stream.
    pub fn prepend<T: Into<TokenTree>>(&mut self, token: T) {
        let mut new_stream = TokenStream::new();
        new_stream.extend(Some(token.into()));
        new_stream.extend(self.inner.clone());
        self.inner = new_stream;
    }

    /// Returns true if the stream is empty.
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Returns an iterator over the token trees.
    pub fn iter(&self) -> impl Iterator<Item = TokenTree> + '_ {
        self.inner.clone().into_iter()
    }

    /// Returns the number of token trees in the stream.
    pub fn len(&self) -> usize {
        self.inner.clone().into_iter().count()
    }

    /// Returns all ident-like tokens in the stream.
    pub fn get_idents(&self) -> Vec<Ident> {
        self.inner
            .clone()
            .into_iter()
            .filter_map(|tt| {
                if let TokenTree::Ident(ident) = tt {
                    Some(ident)
                } else {
                    None
                }
            })
            .collect()
    }

    /// Returns all literal tokens in the stream.
    pub fn get_literals(&self) -> Vec<Literal> {
        self.inner
            .clone()
            .into_iter()
            .filter_map(|tt| {
                if let TokenTree::Literal(lit) = tt {
                    Some(lit)
                } else {
                    None
                }
            })
            .collect()
    }

    /// Returns all punctuation tokens in the stream.
    pub fn get_puncts(&self) -> Vec<Punct> {
        self.inner
            .clone()
            .into_iter()
            .filter_map(|tt| {
                if let TokenTree::Punct(punct) = tt {
                    Some(punct)
                } else {
                    None
                }
            })
            .collect()
    }

    /// Returns all group tokens in the stream.
    pub fn get_groups(&self) -> Vec<proc_macro2::Group> {
        self.inner
            .clone()
            .into_iter()
            .filter_map(|tt| {
                if let TokenTree::Group(group) = tt {
                    Some(group)
                } else {
                    None
                }
            })
            .collect()
    }

    /// Creates an ident from a string with the current span.
    pub fn ident(name: &str) -> Self {
        Self {
            inner: TokenTree::Ident(Ident::new(name, Span::call_site())).into(),
        }
    }

    /// Creates an ident with a specific span.
    pub fn ident_at(name: &str, span: Span) -> Self {
        Self {
            inner: TokenTree::Ident(Ident::new(name, span)).into(),
        }
    }

    /// Creates a literal integer with a specific span.
    pub fn literal_int_at(s: &str, span: Span) -> Self {
        let lit = if let Ok(val) = s.parse::<i64>() {
            let mut l = Literal::i64_unsuffixed(val);
            l.set_span(span);
            l
        } else if let Ok(val) = s.parse::<u64>() {
            let mut l = Literal::u64_unsuffixed(val);
            l.set_span(span);
            l
        } else {
            let mut l = Literal::i32_unsuffixed(s.parse::<i32>().unwrap_or(0));
            l.set_span(span);
            l
        };
        Self {
            inner: TokenTree::Literal(lit).into(),
        }
    }

    /// Creates a literal string from a string with the current span.
    pub fn literal_string(s: &str) -> Self {
        Self {
            inner: TokenTree::Literal(Literal::string(s)).into(),
        }
    }

    /// Creates a literal string with a specific span.
    pub fn literal_string_at(s: &str, span: Span) -> Self {
        let mut lit = Literal::string(s);
        lit.set_span(span);
        Self {
            inner: TokenTree::Literal(lit).into(),
        }
    }

    /// Creates a punct token from a character.
    pub fn punct(c: char) -> Self {
        Self {
            inner: TokenTree::Punct(Punct::new(c, Spacing::Alone)).into(),
        }
    }

    /// Creates a punct token with specific spacing.
    pub fn punct_spaced(c: char, spacing: Spacing) -> Self {
        Self {
            inner: TokenTree::Punct(Punct::new(c, spacing)).into(),
        }
    }

    /// Joins multiple token streams with commas.
    pub fn join_comma(trees: impl IntoIterator<Item = TokenStreamWrapper>) -> Self {
        let mut result = Self::new();
        let mut trees = trees.into_iter().peekable();
        while let Some(tree) = trees.next() {
            result.append_stream(&tree);
            if trees.peek().is_some() {
                let comma = Punct::new(',', Spacing::Alone);
                result.append(comma);
            }
        }
        result
    }

    /// Joins multiple token streams with a separator.
    pub fn join(
        trees: impl IntoIterator<Item = TokenStreamWrapper>,
        separator: &str,
    ) -> Self {
        let mut result = Self::new();
        let mut trees = trees.into_iter().peekable();
        while let Some(tree) = trees.next() {
            result.append_stream(&tree);
            if trees.peek().is_some() {
                for c in separator.chars() {
                    let punct = Punct::new(c, Spacing::Alone);
                    result.append(punct);
                }
            }
        }
        result
    }

    /// Wraps the stream in parentheses.
    pub fn wrap_parens(&self) -> Self {
        let inner = self.inner.clone();
        let group = proc_macro2::Group::new(proc_macro2::Delimiter::Parenthesis, inner);
        let mut result = Self::new();
        result.append(TokenTree::Group(group));
        result
    }

    /// Wraps the stream in braces.
    pub fn wrap_braces(&self) -> Self {
        let inner = self.inner.clone();
        let group = proc_macro2::Group::new(proc_macro2::Delimiter::Brace, inner);
        let mut result = Self::new();
        result.append(TokenTree::Group(group));
        result
    }

    /// Wraps the stream in brackets.
    pub fn wrap_brackets(&self) -> Self {
        let inner = self.inner.clone();
        let group = proc_macro2::Group::new(proc_macro2::Delimiter::Bracket, inner);
        let mut result = Self::new();
        result.append(TokenTree::Group(group));
        result
    }
}

impl Default for TokenStreamWrapper {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Display for TokenStreamWrapper {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl From<TokenStream> for TokenStreamWrapper {
    fn from(stream: TokenStream) -> Self {
        Self { inner: stream }
    }
}

impl From<TokenStreamWrapper> for TokenStream {
    fn from(wrapper: TokenStreamWrapper) -> Self {
        wrapper.inner
    }
}

impl From<TokenTree> for TokenStreamWrapper {
    fn from(tree: TokenTree) -> Self {
        let mut stream = TokenStream::new();
        stream.extend(Some(tree));
        Self { inner: stream }
    }
}

impl From<Ident> for TokenStreamWrapper {
    fn from(ident: Ident) -> Self {
        Self {
            inner: TokenTree::Ident(ident).into(),
        }
    }
}

impl From<Literal> for TokenStreamWrapper {
    fn from(literal: Literal) -> Self {
        Self {
            inner: TokenTree::Literal(literal).into(),
        }
    }
}

impl From<Punct> for TokenStreamWrapper {
    fn from(punct: Punct) -> Self {
        Self {
            inner: TokenTree::Punct(punct).into(),
        }
    }
}

impl FromIterator<TokenTree> for TokenStreamWrapper {
    fn from_iter<T: IntoIterator<Item = TokenTree>>(iter: T) -> Self {
        Self {
            inner: iter.into_iter().collect(),
        }
    }
}

impl quote::ToTokens for TokenStreamWrapper {
    fn to_tokens(&self, tokens: &mut TokenStream) {
        tokens.extend(self.inner.clone());
    }

    fn to_token_stream(&self) -> TokenStream {
        self.inner.clone()
    }

    fn into_token_stream(self) -> TokenStream {
        self.inner
    }
}

/// Parses a string into a token stream, providing a stable interface
/// for string-to-token conversion that works both inside and outside
/// of procedural macro contexts.
pub fn parse_str(input: &str) -> Result<TokenStreamWrapper, String> {
    use proc_macro2::Punct;

    let mut result = TokenStream::new();
    let chars: Vec<char> = input.chars().collect();
    let len = chars.len();
    let mut i = 0;

    while i < len {
        let ch = chars[i];
        if ch.is_whitespace() {
            i += 1;
        } else if ch.is_alphabetic() || ch == '_' {
            // Collect identifier
            let start = i;
            while i < len && (chars[i].is_alphanumeric() || chars[i] == '_') {
                i += 1;
            }
            let ident_str: String = chars[start..i].iter().collect();
            result.extend(Some(TokenTree::Ident(Ident::new(&ident_str, Span::call_site()))));
        } else if ch.is_ascii_digit() {
            // Collect literal
            let start = i;
            while i < len && chars[i].is_ascii_digit() {
                i += 1;
            }
            let lit_str: String = chars[start..i].iter().collect();
            if let Ok(n) = lit_str.parse::<i64>() {
                result.extend(Some(TokenTree::Literal(Literal::i64_unsuffixed(n))));
            } else if let Ok(n) = lit_str.parse::<u64>() {
                result.extend(Some(TokenTree::Literal(Literal::u64_unsuffixed(n))));
            }
        } else if ch == '"' {
            // Collect string literal
            i += 1;
            let start = i;
            while i < len && chars[i] != '"' {
                i += 1;
            }
            let str_str: String = chars[start..i].iter().collect();
            result.extend(Some(TokenTree::Literal(Literal::string(&str_str))));
            if i < len {
                i += 1; // skip closing quote
            }
        } else {
            // Single character token
            let next_spacing = if i + 1 < len && (chars[i + 1].is_alphanumeric() || chars[i + 1] == '_') {
                Spacing::Joint
            } else {
                Spacing::Alone
            };
            let punct = Punct::new(ch, next_spacing);
            result.extend(Some(TokenTree::Punct(punct)));
            i += 1;
        }
    }

    Ok(TokenStreamWrapper { inner: result })
}

/// Provides a convenience function for creating token streams from
/// ident-only inputs, with error handling for stable contexts.
pub fn parse_ident(input: &str) -> Result<Ident, String> {
    let wrapper = parse_str(input.trim())?;
    let idents = wrapper.get_idents();
    if idents.is_empty() {
        Err("expected ident, found empty or non-ident token".to_string())
    } else {
        Ok(idents[0].clone())
    }
}

#[cfg(test)]
    mod tests {
        use super::*;
        use std::str::FromStr;
        use quote::ToTokens;

    #[test]
    fn test_new_and_empty() {
        let stream = TokenStreamWrapper::new();
        assert!(stream.is_empty());
        assert_eq!(stream.len(), 0);
    }

    #[test]
    fn test_ident() {
        let wrapper = TokenStreamWrapper::ident("foo");
        let idents = wrapper.get_idents();
        assert_eq!(idents.len(), 1);
        assert_eq!(idents[0].to_string(), "foo");
    }

    #[test]
    fn test_append() {
        let mut wrapper = TokenStreamWrapper::new();
        wrapper.append_stream(&TokenStreamWrapper::ident("foo"));
        wrapper.append_stream(&TokenStreamWrapper::punct(','));
        wrapper.append_stream(&TokenStreamWrapper::ident("bar"));

        let idents = wrapper.get_idents();
        assert_eq!(idents.len(), 2);
        assert_eq!(idents[0].to_string(), "foo");
        assert_eq!(idents[1].to_string(), "bar");
    }

    #[test]
    fn test_wrap_parens() {
        let wrapper = TokenStreamWrapper::ident("foo");
        let wrapped = wrapper.wrap_parens();
        let s = wrapped.to_stream().to_string();
        assert_eq!(s, "(foo)");
    }

    #[test]
    fn test_wrap_braces() {
        let wrapper = TokenStreamWrapper::ident("foo");
        let wrapped = wrapper.wrap_braces();
        let s = wrapped.to_stream().to_string();
        assert_eq!(s, "{ foo }");
    }

    #[test]
    fn test_wrap_brackets() {
        let wrapper = TokenStreamWrapper::ident("foo");
        let wrapped = wrapper.wrap_brackets();
        let s = wrapped.to_stream().to_string();
        assert_eq!(s, "[foo]");
    }

    #[test]
    fn test_parse_str() {
        let wrapper = parse_str("let x = 42;").unwrap();
        assert!(!wrapper.is_empty());
    }

    #[test]
    fn test_join_comma() {
        let trees = vec![
            TokenStreamWrapper::ident("a"),
            TokenStreamWrapper::ident("b"),
            TokenStreamWrapper::ident("c"),
        ];
        let joined = TokenStreamWrapper::join_comma(trees);
        let s = joined.to_stream().to_string();
        assert!(s.contains("a"));
        assert!(s.contains("b"));
        assert!(s.contains("c"));
    }

    #[test]
    fn test_from_stream() {
        let stream = TokenStream::from_str("foo").unwrap();
        let wrapper = TokenStreamWrapper::from(stream);
        let idents = wrapper.get_idents();
        assert_eq!(idents.len(), 1);
    }

    #[test]
    fn test_display() {
        let wrapper = TokenStreamWrapper::ident("hello");
        assert_eq!(wrapper.to_string(), "hello");
    }

    #[test]
    fn test_to_tokens() {
        let wrapper = TokenStreamWrapper::ident("test");
        let mut out = TokenStream::new();
        wrapper.to_tokens(&mut out);
        assert!(!out.is_empty());
    }
}