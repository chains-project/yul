//! A stable, usable-outside-the-compiler wrapper around Rust's token stream API.
//!
//! The compiler's own `proc_macro` API is only available inside a procedural
//! macro crate, and many of its entry points are unstable. This crate builds on
//! [`proc_macro2`] to offer the same token-stream model in any context: a
//! `proc-macro` crate, a `build.rs`, a test, or a plain binary.
//!
//! The wrapper is intentionally a normal library crate so that its helpers can
//! be unit-tested and reused outside the compiler. The companion
//! `stable-tokens-macros` crate exposes them as real procedural macros.

use proc_macro2::{TokenStream, TokenTree};

pub use proc_macro2;

/// Count the token trees at the top level of `tokens`, treating a delimited
/// group (such as `(a b)`) as a single tree.
pub fn token_tree_count(tokens: TokenStream) -> usize {
    tokens.into_iter().count()
}

/// Recursively count every token tree in `tokens`, descending into delimited
/// groups.
pub fn token_count(tokens: TokenStream) -> usize {
    tokens
        .into_iter()
        .map(|tree| match tree {
            TokenTree::Group(group) => 1 + token_count(group.stream()),
            _ => 1,
        })
        .sum()
}

/// Flatten `tokens` into a single sequence, discarding all delimiter groups.
pub fn flatten(tokens: TokenStream) -> TokenStream {
    let mut flattened = TokenStream::new();
    for tree in tokens {
        match tree {
            TokenTree::Group(group) => flattened.extend(flatten(group.stream())),
            other => flattened.extend(std::iter::once(other)),
        }
    }
    flattened
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse(source: &str) -> TokenStream {
        source.parse().expect("valid token stream")
    }

    #[test]
    fn counts_top_level_trees() {
        assert_eq!(token_tree_count(parse("a + b (c d)")), 4);
    }

    #[test]
    fn counts_recursively() {
        assert_eq!(token_count(parse("a + b (c d)")), 6);
    }

    #[test]
    fn flattens_groups() {
        assert_eq!(flatten(parse("a (b c)")).to_string(), "a b c");
    }
}
