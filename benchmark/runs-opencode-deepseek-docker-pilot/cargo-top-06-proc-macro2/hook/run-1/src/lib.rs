//! A procedural macro crate.
//!
//! The compiler-facing entry points live here and use `proc_macro`. All real
//! work is done against `proc_macro2::TokenStream` so it can be built and tested
//! outside of the compiler.

use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput};

mod expand;

/// Derives an inherent `hello()` returning the annotated type's name.
#[proc_macro_derive(Hello)]
pub fn derive_hello(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand::derive_hello(&input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}
