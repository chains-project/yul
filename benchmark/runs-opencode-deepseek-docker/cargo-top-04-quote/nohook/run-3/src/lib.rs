//! Procedural macros that build Rust source code as token streams.
//!
//! This crate demonstrates the standard codegen stack:
//!
//! * [`proc_macro2`] - a stable, testable wrapper around `proc_macro`.
//! * [`syn`] - parses the incoming tokens into an AST.
//! * [`quote`] - turns a Rust-like template back into a `TokenStream`.
//!
//! A proc-macro crate may only export macros, so everything generated here
//! targets standard Rust items (free functions, constants, inherent impls).

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::{format_ident, quote};
use syn::{parse_macro_input, DeriveInput, Ident, LitInt, LitStr};

/// Generates a function named by the supplied identifier.
///
/// ```ignore
/// make_fn!(greet);
/// assert_eq!(greet(), "greet");
/// ```
#[proc_macro]
pub fn make_fn(input: TokenStream) -> TokenStream {
    let name = parse_macro_input!(input as Ident);
    let generated: TokenStream2 = quote! {
        pub fn #name() -> &'static str {
            stringify!(#name)
        }
    };
    generated.into()
}

/// Generates `count` public constants (`CONST_0`, `CONST_1`, ...) whose values
/// match their index.
///
/// This builds the token stream programmatically instead of using `quote!`
/// for the repetition, which is useful when the shape is dynamic.
#[proc_macro]
pub fn make_consts(input: TokenStream) -> TokenStream {
    let count = parse_macro_input!(input as LitInt);
    let count: usize = count
        .base10_parse()
        .expect("`make_consts!` expects a non-negative integer literal");

    let consts = (0..count).map(|i| {
        let ident = format_ident!("CONST_{i}");
        let value = i as u64;
        quote! {
            pub const #ident: u64 = #value;
        }
    });

    quote! { #(#consts)* }.into()
}

/// Derives an inherent `describe` method returning a short type description.
///
/// ```ignore
/// #[derive(Describe)]
/// struct Widget;
///
/// assert_eq!(Widget.describe(), "a struct named Widget");
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;

    let text = match &input.data {
        syn::Data::Struct(_) => format!("a struct named {name}"),
        syn::Data::Enum(_) => format!("an enum named {name}"),
        syn::Data::Union(_) => format!("a union named {name}"),
    };
    let text = LitStr::new(&text, name.span());

    let expanded = quote! {
        impl #name {
            pub fn describe(&self) -> &'static str {
                #text
            }
        }
    };
    expanded.into()
}
