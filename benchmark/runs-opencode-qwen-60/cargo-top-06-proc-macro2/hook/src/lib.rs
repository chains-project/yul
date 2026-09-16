//! A stable, usable-outside-the-compiler wrapper around Rust's token stream API.
//!
//! This crate provides a unified API for working with Rust procedural macro token streams
//! that works both inside proc-macro crates and in regular library crates. It uses
//! [`proc-macro2`] internally to provide a stable interface independent of the compiler's
//! internal representation.
//!
//! # Dual Context Support
//!
//! This crate works in two contexts thanks to `proc-macro2`:
//! - **Inside proc-macro crates**: Delegates to the compiler's native `proc_macro` types.
//! - **In regular library crates**: Uses `proc-macro2`'s standalone implementation.
//!
//! In both cases, the API is identical, providing a stable surface area.
//!
//! # Example
//!
//! ```
//! use token_stream_wrapper::{TokenStream, TokenTree, Ident};
//!
//! let stream = TokenStream::from_str("fn main() {}").unwrap();
//!
//! for token in stream.iter() {
//!     match token {
//!         TokenTree::Ident(ident) => println!("Ident: {}", ident),
//!         TokenTree::Punct(punct) => println!("Punct: {}", punct),
//!         _ => {}
//!     }
//! }
//!
//! println!("{}", stream);
//! ```

use proc_macro2::{
    Group as RawGroup, Ident as RawIdent, Literal as RawLiteral, Punct as RawPunct,
    Span as RawSpan, TokenStream as RawTokenStream, TokenTree as RawTokenTree,
    lex::Error as RawLexError,
};
use std::fmt;
use std::str::FromStr;

// ===========================================================================
// TokenTreeIter
// ===========================================================================

/// An iterator over [`TokenTree`] items in a [`TokenStream`].
pub struct TokenTreeIter {
    tokens: Vec<RawTokenTree>,
    index: usize,
}

impl Iterator for TokenTreeIter {
    type Item = TokenTree;

    fn next(&mut self) -> Option<Self::Item> {
        if self.index < self.tokens.len() {
            let tt = self.tokens[self.index].clone();
            self.index += 1;
            Some(convert_token_tree(tt))
        } else {
            None
        }
    }

    fn size_hint(&self) -> (usize, Option<usize>) {
        let remaining = self.tokens.len() - self.index;
        (remaining, Some(remaining))
    }
}

impl ExactSizeIterator for TokenTreeIter {}

impl Clone for TokenTreeIter {
    fn clone(&self) -> Self {
        TokenTreeIter {
            tokens: self.tokens.clone(),
            index: self.index,
        }
    }
}

// ===========================================================================
// TokenStream
// ===========================================================================

/// A stable token stream wrapper.
///
/// Wraps [`proc_macro2::TokenStream`] to provide a stable API that works both
/// inside and outside proc-macro contexts, independent of the compiler's
/// internal representation.
#[non_exhaustive]
pub struct TokenStream {
    inner: RawTokenStream,
}

impl TokenStream {
    /// Creates a new empty token stream.
    pub fn new() -> Self {
        TokenStream {
            inner: RawTokenStream::new(),
        }
    }

    /// Creates a token stream from a string representation.
    ///
    /// # Errors
    ///
    /// Returns [`LexError`] if the string contains invalid tokens.
    ///
    /// # Example
    ///
    /// ```
    /// use token_stream_wrapper::TokenStream;
    ///
    /// let stream = TokenStream::from_str("fn main() {}").unwrap();
    /// assert!(!stream.is_empty());
    /// ```
    pub fn from_str(s: &str) -> Result<Self, LexError> {
        RawTokenStream::from_str(s)
            .map(|inner| TokenStream { inner })
            .map_err(LexError)
    }

    /// Returns `true` if the token stream contains no tokens.
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }

    /// Returns the number of top-level tokens in the stream.
    pub fn len(&self) -> usize {
        self.inner.clone().into_iter().count()
    }

    /// Returns an iterator over the token trees in the stream.
    pub fn iter(&self) -> TokenTreeIter {
        TokenTreeIter {
            tokens: self.inner.clone().into_iter().collect(),
            index: 0,
        }
    }

    /// Converts the token stream to its string representation.
    pub fn to_string(&self) -> String {
        format!("{}", self.inner)
    }

    /// Consumes the token stream and returns the underlying [`RawTokenStream`].
    pub fn into_inner(self) -> RawTokenStream {
        self.inner
    }

    /// Creates a [`TokenStream`] from the underlying [`RawTokenStream`].
    pub fn from_inner(inner: RawTokenStream) -> Self {
        TokenStream { inner }
    }
}

impl Default for TokenStream {
    fn default() -> Self {
        Self::new()
    }
}

impl fmt::Display for TokenStream {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl FromStr for TokenStream {
    type Err = LexError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Self::from_str(s)
    }
}

impl From<RawTokenStream> for TokenStream {
    fn from(inner: RawTokenStream) -> Self {
        TokenStream { inner }
    }
}

impl From<TokenStream> for RawTokenStream {
    fn from(ts: TokenStream) -> Self {
        ts.inner
    }
}

impl Clone for TokenStream {
    fn clone(&self) -> Self {
        TokenStream {
            inner: self.inner.clone(),
        }
    }
}

impl IntoIterator for TokenStream {
    type Item = TokenTree;
    type IntoIter = TokenTreeIter;

    fn into_iter(self) -> Self::IntoIter {
        TokenTreeIter {
            tokens: self.inner.into_iter().collect(),
            index: 0,
        }
    }
}

impl<'a> IntoIterator for &'a TokenStream {
    type Item = TokenTree;
    type IntoIter = TokenTreeIter;

    fn into_iter(self) -> Self::IntoIter {
        self.iter()
    }
}

// ===========================================================================
// TokenTree
// ===========================================================================

/// A single token or a delimited group of tokens.
#[non_exhaustive]
pub enum TokenTree {
    /// An identifier (`fn`, `foo`, `bar`)
    Ident(Ident),
    /// A literal (`"hello"`, `1`, `1.0`, `1u16`)
    Literal(Literal),
    /// A group containing a delimited token stream
    Group(Group),
    /// A single punctuation character (`+`, `*`, etc.)
    Punct(Punct),
}

impl TokenTree {
    /// Returns a string representation of this token.
    pub fn to_string(&self) -> String {
        match self {
            TokenTree::Ident(ident) => ident.to_string(),
            TokenTree::Literal(lit) => lit.to_string(),
            TokenTree::Group(group) => group.to_string(),
            TokenTree::Punct(punct) => punct.to_string(),
        }
    }
}

impl fmt::Display for TokenTree {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}

impl Clone for TokenTree {
    fn clone(&self) -> Self {
        match self {
            TokenTree::Ident(ident) => TokenTree::Ident(ident.clone()),
            TokenTree::Literal(lit) => TokenTree::Literal(lit.clone()),
            TokenTree::Group(group) => TokenTree::Group(group.clone()),
            TokenTree::Punct(punct) => TokenTree::Punct(punct.clone()),
        }
    }
}

impl From<Ident> for TokenTree {
    fn from(ident: Ident) -> Self {
        TokenTree::Ident(ident)
    }
}

impl From<Literal> for TokenTree {
    fn from(lit: Literal) -> Self {
        TokenTree::Literal(lit)
    }
}

impl From<Group> for TokenTree {
    fn from(group: Group) -> Self {
        TokenTree::Group(group)
    }
}

impl From<Punct> for TokenTree {
    fn from(punct: Punct) -> Self {
        TokenTree::Punct(punct)
    }
}

// ===========================================================================
// Ident
// ===========================================================================

/// A Rust identifier.
#[non_exhaustive]
pub struct Ident {
    inner: RawIdent,
}

impl Ident {
    /// Creates a new identifier.
    ///
    /// The `span` parameter is used for error reporting and hygienic macro expansion.
    pub fn new(name: &str, span: Span) -> Self {
        Ident {
            inner: RawIdent::new(name, span.inner),
        }
    }

    /// Creates a new raw identifier (prefixed with `r#`).
    pub fn new_raw(name: &str, span: Span) -> Self {
        Ident {
            inner: RawIdent::new_raw(name, span.inner),
        }
    }

    /// Returns the span associated with this identifier.
    pub fn span(&self) -> Span {
        Span { inner: self.inner.span() }
    }

    /// Assigns a span to this identifier.
    pub fn set_span(&mut self, span: Span) {
        self.inner.set_span(span.inner);
    }

    /// Consumes the identifier and returns the underlying [`RawIdent`].
    pub fn into_inner(self) -> RawIdent {
        self.inner
    }

    /// Creates an [`Ident`] from the underlying [`RawIdent`].
    pub fn from_inner(inner: RawIdent) -> Self {
        Ident { inner }
    }
}

impl fmt::Display for Ident {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl fmt::Debug for Ident {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Ident({:?})", self.inner)
    }
}

impl PartialEq for Ident {
    fn eq(&self, other: &Self) -> bool {
        self.inner == other.inner
    }
}

impl Eq for Ident {}

impl Clone for Ident {
    fn clone(&self) -> Self {
        Ident { inner: self.inner.clone() }
    }
}

impl Copy for Ident {}

impl Hash for Ident {
    fn hash<H: std::hash::Hasher>(&self, state: &mut H) {
        self.inner.hash(state);
    }
}

// ===========================================================================
// Literal
// ===========================================================================

/// A Rust literal value (string, number, boolean, etc.).
#[non_exhaustive]
pub struct Literal {
    inner: RawLiteral,
}

impl Literal {
    /// Creates a string literal.
    ///
    /// # Example
    ///
    /// ```
    /// use token_stream_wrapper::Literal;
    ///
    /// let lit = Literal::string("hello");
    /// ```
    pub fn string(s: &str) -> Self {
        Literal {
            inner: RawLiteral::string(s),
        }
    }

    /// Creates a character literal.
    pub fn character(c: char) -> Self {
        Literal {
            inner: RawLiteral::character(c),
        }
    }

    /// Creates an integer literal.
    pub fn integer(n: u64) -> Self {
        Literal {
            inner: RawLiteral::integer(n),
        }
    }

    /// Creates a 32-bit float literal.
    ///
    /// The value will be suffixed with `f32` to ensure correct type.
    pub fn f32(n: f32) -> Self {
        Literal {
            inner: RawLiteral::f32(n),
        }
    }

    /// Creates a 64-bit float literal.
    ///
    /// The value will be suffixed with `f64` to ensure correct type.
    pub fn f64(n: f64) -> Self {
        Literal {
            inner: RawLiteral::f64(n),
        }
    }

    /// Returns the span associated with this literal.
    pub fn span(&self) -> Span {
        Span { inner: self.inner.span() }
    }

    /// Assigns a span to this literal.
    pub fn set_span(&mut self, span: Span) {
        self.inner.set_span(span.inner);
    }

    /// Consumes the literal and returns the underlying [`RawLiteral`].
    pub fn into_inner(self) -> RawLiteral {
        self.inner
    }

    /// Creates a [`Literal`] from the underlying [`RawLiteral`].
    pub fn from_inner(inner: RawLiteral) -> Self {
        Literal { inner }
    }
}

impl fmt::Display for Literal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl fmt::Debug for Literal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Literal({:?})", self.inner)
    }
}

impl Clone for Literal {
    fn clone(&self) -> Self {
        Literal { inner: self.inner.clone() }
    }
}

// ===========================================================================
// Group
// ===========================================================================

/// A delimited group of tokens (e.g., `(a + b)`).
#[non_exhaustive]
pub struct Group {
    inner: RawGroup,
}

impl Group {
    /// Creates a new group with the given delimiter and token stream.
    pub fn new(delimiter: Delimiter, stream: TokenStream) -> Self {
        Group {
            inner: RawGroup::new(delimiter.into(), stream.into_inner()),
        }
    }

    /// Returns the delimiter used by this group.
    pub fn delimiter(&self) -> Delimiter {
        self.inner.delimiter().into()
    }

    /// Returns the token stream contained in this group.
    pub fn stream(&self) -> TokenStream {
        TokenStream { inner: self.inner.stream() }
    }

    /// Returns the span associated with this group.
    pub fn span(&self) -> Span {
        Span { inner: self.inner.span() }
    }

    /// Assigns a span to this group.
    pub fn set_span(&mut self, span: Span) {
        self.inner.set_span(span.inner);
    }

    /// Consumes the group and returns the underlying [`RawGroup`].
    pub fn into_inner(self) -> RawGroup {
        self.inner
    }

    /// Creates a [`Group`] from the underlying [`RawGroup`].
    pub fn from_inner(inner: RawGroup) -> Self {
        Group { inner }
    }
}

impl fmt::Display for Group {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl fmt::Debug for Group {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Group({:?})", self.inner)
    }
}

impl Clone for Group {
    fn clone(&self) -> Self {
        Group { inner: self.inner.clone() }
    }
}

// ===========================================================================
// Punct
// ===========================================================================

/// A single punctuation character (`+`, `*`, etc.).
#[non_exhaustive]
pub struct Punct {
    inner: RawPunct,
}

impl Punct {
    /// Creates a new punctuation character.
    pub fn new(ch: char, spacing: Spacing) -> Self {
        Punct {
            inner: RawPunct::new(ch, spacing.into()),
        }
    }

    /// Returns the character represented by this punctuation.
    pub fn as_char(&self) -> char {
        self.inner.as_char()
    }

    /// Returns the spacing after this punctuation.
    pub fn spacing(&self) -> Spacing {
        self.inner.spacing().into()
    }

    /// Returns the span associated with this punctuation.
    pub fn span(&self) -> Span {
        Span { inner: self.inner.span() }
    }

    /// Assigns a span to this punctuation.
    pub fn set_span(&mut self, span: Span) {
        self.inner.set_span(span.inner);
    }

    /// Consumes the punctuation and returns the underlying [`RawPunct`].
    pub fn into_inner(self) -> RawPunct {
        self.inner
    }

    /// Creates a [`Punct`] from the underlying [`RawPunct`].
    pub fn from_inner(inner: RawPunct) -> Self {
        Punct { inner }
    }
}

impl fmt::Display for Punct {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.inner)
    }
}

impl fmt::Debug for Punct {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Punct({:?})", self.inner)
    }
}

impl Clone for Punct {
    fn clone(&self) -> Self {
        Punct { inner: self.inner.clone() }
    }
}

impl PartialEq for Punct {
    fn eq(&self, other: &Self) -> bool {
        self.inner == other.inner
    }
}

impl Eq for Punct {}

// ===========================================================================
// Span
// ===========================================================================

/// A span encapsulating a source code range.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Span {
    inner: RawSpan,
}

impl Span {
    /// Returns the span corresponding to the call site of the method where
    /// `Span::call_site()` is invoked.
    pub fn call_site() -> Self {
        Span { inner: RawSpan::call_site() }
    }

    /// Returns the span corresponding to the invocation of the macro that
    /// expanded declaratively.
    pub fn mixed_site() -> Self {
        Span { inner: RawSpan::mixed_site() }
    }

    /// Returns the span corresponding to the definition of the current
    /// procedural macro.
    pub fn def_site() -> Self {
        Span { inner: RawSpan::def_site() }
    }

    /// Returns a span that resolves at the location where `self` is defined.
    pub fn resolved_at(&self, other: Span) -> Self {
        Span {
            inner: self.inner.resolved_at(other.inner),
        }
    }

    /// Returns a span that is located at the location where `other` is defined.
    pub fn located_at(&self, other: Span) -> Self {
        Span {
            inner: self.inner.located_at(other.inner),
        }
    }

    /// Consumes the span and returns the underlying [`RawSpan`].
    pub fn unwrap(self) -> RawSpan {
        self.inner
    }

    /// Creates a [`Span`] from the underlying [`RawSpan`].
    pub fn from_inner(inner: RawSpan) -> Self {
        Span { inner }
    }
}

impl fmt::Display for Span {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self.inner)
    }
}

// ===========================================================================
// Delimiter
// ===========================================================================

/// The delimiter of a [`Group`].
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Delimiter {
    /// Parentheses: `(...)`
    Parenthesis,
    /// Square brackets: `[...]`
    Bracket,
    /// Braces: `{...}`
    Brace,
    /// No delimiter
    None,
}

impl fmt::Display for Delimiter {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Delimiter::Parenthesis => write!(f, "()"),
            Delimiter::Bracket => write!(f, "[]"),
            Delimiter::Brace => write!(f, "{{}}"),
            Delimiter::None => write!(f, ""),
        }
    }
}

impl From<proc_macro2::Delimiter> for Delimiter {
    fn from(d: proc_macro2::Delimiter) -> Self {
        match d {
            proc_macro2::Delimiter::Parenthesis => Delimiter::Parenthesis,
            proc_macro2::Delimiter::Bracket => Delimiter::Bracket,
            proc_macro2::Delimiter::Brace => Delimiter::Brace,
            proc_macro2::Delimiter::None => Delimiter::None,
        }
    }
}

impl From<Delimiter> for proc_macro2::Delimiter {
    fn from(d: Delimiter) -> Self {
        match d {
            Delimiter::Parenthesis => proc_macro2::Delimiter::Parenthesis,
            Delimiter::Bracket => proc_macro2::Delimiter::Bracket,
            Delimiter::Brace => proc_macro2::Delimiter::Brace,
            Delimiter::None => proc_macro2::Delimiter::None,
        }
    }
}

// ===========================================================================
// Spacing
// ===========================================================================

/// The spacing after a [`Punct`].
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Spacing {
    /// The punctuation is followed by another token without whitespace.
    Continuous,
    /// The punctuation is followed by whitespace or another token.
    Alone,
}

impl fmt::Display for Spacing {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Spacing::Continuous => write!(f, "continuous"),
            Spacing::Alone => write!(f, "alone"),
        }
    }
}

impl From<proc_macro2::Spacing> for Spacing {
    fn from(s: proc_macro2::Spacing) -> Self {
        match s {
            proc_macro2::Spacing::Alone => Spacing::Alone,
            proc_macro2::Spacing::Continuous => Spacing::Continuous,
        }
    }
}

impl From<Spacing> for proc_macro2::Spacing {
    fn from(s: Spacing) -> Self {
        match s {
            Spacing::Alone => proc_macro2::Spacing::Alone,
            Spacing::Continuous => proc_macro2::Spacing::Continuous,
        }
    }
}

// ===========================================================================
// LexError
// ===========================================================================

/// An error that occurs when parsing a token stream from a string.
#[non_exhaustive]
pub struct LexError(RawLexError);

impl fmt::Display for LexError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "lexical error parsing token stream")
    }
}

impl std::error::Error for LexError {}

impl fmt::Debug for LexError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "LexError")
    }
}

// ===========================================================================
// Helper functions
// ===========================================================================

fn convert_token_tree(tt: RawTokenTree) -> TokenTree {
    match tt {
        RawTokenTree::Ident(ident) => TokenTree::Ident(Ident { inner: ident }),
        RawTokenTree::Literal(lit) => TokenTree::Literal(Literal { inner: lit }),
        RawTokenTree::Group(group) => TokenTree::Group(Group { inner: group }),
        RawTokenTree::Punct(punct) => TokenTree::Punct(Punct { inner: punct }),
    }
}

// Re-export proc_macro2 types for users who need them directly.
// These are useful when interoperating with other proc-macro ecosystem crates.
#[doc(hidden)]
pub use proc_macro2 as raw;