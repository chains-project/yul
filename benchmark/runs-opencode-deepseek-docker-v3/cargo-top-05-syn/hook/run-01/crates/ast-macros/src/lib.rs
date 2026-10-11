//! Procedural macros backed by [`ast_core`].
//!
//! This crate is deliberately a thin facade: all parsing, inspection, and
//! transformation lives in `ast-core`, which can be unit-tested like an
//! ordinary library.

use ast_core::{inspect, transform};
use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::parse::Parser;
use syn::punctuated::Punctuated;
use syn::{parse_macro_input, File, Ident, Token};

/// Rename an identifier throughout the annotated item.
///
/// ```ignore
/// #[ast_macros::rename(a, x)]
/// fn add(a: i32, b: i32) -> i32 {
///     a + b
/// }
/// // expands to `fn add(x: i32, b: i32) -> i32 { x + b }`
/// ```
#[proc_macro_attribute]
pub fn rename(attr: TokenStream, item: TokenStream) -> TokenStream {
    match rename_impl(attr, item) {
        Ok(tokens) => tokens.into(),
        Err(err) => err.to_compile_error().into(),
    }
}

fn rename_impl(attr: TokenStream, item: TokenStream) -> syn::Result<TokenStream2> {
    let args = Punctuated::<Ident, Token![,]>::parse_terminated.parse(attr)?;
    let mut args = args.into_iter();
    let from = args.next().ok_or_else(|| {
        syn::Error::new(
            proc_macro2::Span::call_site(),
            "expected `#[rename(old, new)]`",
        )
    })?;
    let to = args.next().ok_or_else(|| {
        syn::Error::new(
            proc_macro2::Span::call_site(),
            "expected `#[rename(old, new)]`",
        )
    })?;

    let mut file: File = syn::parse(item)?;
    transform::rename_in_file(&mut file, &from.to_string(), &to.to_string());
    Ok(quote!(#file))
}

/// Parse the given items and expand to a human-readable summary of the
/// identifiers they contain.
///
/// Useful as a `const` initializer:
///
/// ```ignore
/// const INFO: &str = ast_macros::ast_info!(fn add(a: i32, b: i32) -> i32 { a + b });
/// ```
#[proc_macro]
pub fn ast_info(input: TokenStream) -> TokenStream {
    let file = parse_macro_input!(input as File);
    let report = format!(
        "items={} idents=[{}]",
        inspect::item_count(&file),
        inspect::collect_identifiers(&file).join(", "),
    );
    quote!(#report).into()
}
