//! Procedural macros built on the [`stable_tokens`] wrapper.
//!
//! These entry points stay deliberately thin: they convert the compiler's
//! `proc_macro::TokenStream` into the stable wrapper's `proc_macro2::TokenStream`,
//! delegate to library code, and convert the result back.

use proc_macro::TokenStream;

/// Expand to an integer literal holding the recursive token count of the input.
///
/// ```
/// # use stable_tokens_macros::count_tokens;
/// assert_eq!(count_tokens!(a + b (c d)), 6);
/// ```
#[proc_macro]
pub fn count_tokens(input: TokenStream) -> TokenStream {
    let count = stable_tokens::token_count(input.into());
    count.to_string().parse().expect("integer literal")
}

/// Expand to the input tokens with every delimiter group flattened away.
#[proc_macro]
pub fn flatten_tokens(input: TokenStream) -> TokenStream {
    stable_tokens::flatten(input.into()).into()
}
