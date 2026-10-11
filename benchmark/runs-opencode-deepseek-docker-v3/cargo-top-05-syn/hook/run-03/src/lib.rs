//! Parse Rust source into a [`syn`] syntax tree, inspect it, and expand a
//! transformed version back into tokens.
//!
//! This crate is a thin proc-macro front end. The reusable parsing and
//! transformation logic lives in the [`passes`] module so it can be unit tested
//! without going through the compiler's macro expansion.

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, File};

mod passes;

/// Parse the input as a Rust source file, run every transformation pass, and
/// expand to the rewritten items.
///
/// ```ignore
/// ast_transform::transform! {
///     fn greet() -> &'static str { "hello" }
/// }
/// ```
#[proc_macro]
pub fn transform(input: TokenStream) -> TokenStream {
    let file = parse_macro_input!(input as File);
    let file = passes::transform_file(file);
    quote!(#file).into()
}
