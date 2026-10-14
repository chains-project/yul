//! Procedural macros for this crate.
//!
//! Each macro uses the same pattern: the `#[proc_macro*]` entry point only
//! converts between `proc_macro::TokenStream` (which works only inside the
//! compiler) and `proc_macro2::TokenStream` (a stable wrapper that also works
//! outside it). The real logic runs on `proc_macro2` types, so you can unit
//! test it with plain `cargo test`.

use proc_macro2::TokenStream;

/// Expands to its input unchanged. Replace this with real logic.
#[proc_macro]
pub fn passthrough(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
    passthrough_impl(input.into()).into()
}

fn passthrough_impl(input: TokenStream) -> TokenStream {
    input
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::str::FromStr;

    #[test]
    fn passthrough_preserves_tokens() {
        let input = TokenStream::from_str("let x = 1 + 2;").unwrap();
        let output = passthrough_impl(input.clone());
        assert_eq!(output.to_string(), input.to_string());
    }
}
