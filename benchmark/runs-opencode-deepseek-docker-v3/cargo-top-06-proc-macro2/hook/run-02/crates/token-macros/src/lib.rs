//! Thin proc-macro entry points.
//!
//! This crate exists only to expose the compiler-facing `proc_macro` ABI. All
//! logic is delegated to [`token_core`], which is built on `proc-macro2` and can
//! be exercised by ordinary unit tests.

use proc_macro::TokenStream;

/// Derives an inherent `hello()` method that returns the type's name.
#[proc_macro_derive(Hello)]
pub fn hello(input: TokenStream) -> TokenStream {
    token_core::expand_hello(input.into()).into()
}
