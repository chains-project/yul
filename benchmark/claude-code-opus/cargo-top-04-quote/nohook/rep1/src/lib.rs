//! Procedural macros that generate Rust code as `TokenStream`s.
//!
//! Proc-macro crates can only export macros, so the real logic lives in
//! [`describe`] using `proc_macro2` types, which keeps it unit-testable
//! outside of a compiler invocation.

use proc_macro::TokenStream;
use syn::{DeriveInput, parse_macro_input};

mod describe;

/// Derives an inherent `describe()` method and a `FIELD_NAMES` constant.
///
/// ```
/// use codegen_macros::Describe;
///
/// #[derive(Describe)]
/// struct Point { x: i32, y: i32 }
///
/// assert_eq!(Point::FIELD_NAMES, &["x", "y"]);
/// assert_eq!(Point { x: 1, y: 2 }.describe(), "Point { x: 1, y: 2 }");
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    describe::expand(&input)
        .unwrap_or_else(syn::Error::into_compile_error)
        .into()
}
