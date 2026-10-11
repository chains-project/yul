//! Procedural macros backed by the `rust-transform` crate.
//!
//! Each macro is a thin wrapper: it parses its input into a `syn` tree,
//! calls into `rust-transform` to inspect or mutate that tree, then emits the
//! result with `quote!`.

use proc_macro::TokenStream;
use quote::quote;
use rust_transform::{double_int_literals_file, double_int_literals_item_fn};
use syn::parse_macro_input;

/// Attribute macro that doubles every integer literal in a function body.
///
/// ```ignore
/// #[double_literals]
/// fn answer() -> i32 { 21 } // becomes `{ 42 }`
/// ```
#[proc_macro_attribute]
pub fn double_literals(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let mut item_fn = parse_macro_input!(item as syn::ItemFn);
    double_int_literals_item_fn(&mut item_fn);
    quote!(#item_fn).into()
}

/// Function-like macro that parses a sequence of items and doubles every
/// integer literal, emitting the transformed items.
#[proc_macro]
pub fn double_literals_in_file(input: TokenStream) -> TokenStream {
    let mut file = parse_macro_input!(input as syn::File);
    double_int_literals_file(&mut file);
    quote!(#file).into()
}

/// Function-like macro that parses a sequence of items and expands to an
/// array of the names of all functions it found.
#[proc_macro]
pub fn inspect_fn_names(input: TokenStream) -> TokenStream {
    let file = parse_macro_input!(input as syn::File);
    let names = rust_transform::collect_fn_names(&file);
    let names = names
        .iter()
        .map(|name| syn::LitStr::new(name, proc_macro2::Span::call_site()));
    quote! { [ #(#names),* ] }.into()
}
