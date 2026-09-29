//! A procedural-macro crate built on a stable token stream abstraction.
//!
//! The Rust compiler's native `proc_macro` API is only usable inside a
//! procedural macro. Anything that wants to build or inspect tokens in an
//! ordinary library, a test, or a build script needs a wrapper that does not
//! depend on the compiler's private context. `proc-macro2` is that wrapper: it
//! provides `TokenStream` and friends as stable, compiler-independent types
//! that can be created and manipulated anywhere, then converted to the native
//! `proc_macro::TokenStream` at the macro boundary.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{Data, DeriveInput, Fields, parse_macro_input};

/// Derive a `describe` associated function returning the item's name and the
/// names of its fields.
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    describe(input).into()
}

/// Build the generated `impl` from parsed input.
///
/// This works entirely in terms of `proc_macro2`/`syn` types, so it can be
/// exercised in unit tests without the compiler.
fn describe(input: DeriveInput) -> TokenStream2 {
    let ident = input.ident;
    let type_name = ident.to_string();
    let field_names: Vec<String> = match input.data {
        Data::Struct(data) => match data.fields {
            Fields::Named(fields) => fields
                .named
                .iter()
                .filter_map(|field| field.ident.as_ref())
                .map(ToString::to_string)
                .collect(),
            Fields::Unnamed(fields) => (0..fields.unnamed.len()).map(|i| i.to_string()).collect(),
            Fields::Unit => Vec::new(),
        },
        Data::Enum(_) | Data::Union(_) => Vec::new(),
    };
    let field_names = field_names.iter().map(|name| quote!(#name));

    quote! {
        impl #ident {
            pub fn describe() -> (&'static str, &'static [&'static str]) {
                (#type_name, &[#(#field_names),*])
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn emits_type_and_field_names() {
        let input: DeriveInput = syn::parse_quote! {
            struct Point {
                x: i32,
                y: i32,
            }
        };

        let generated = describe(input).to_string();

        assert!(
            generated.contains("Point"),
            "missing type name: {generated}"
        );
        assert!(generated.contains("\"x\""), "missing field x: {generated}");
        assert!(generated.contains("\"y\""), "missing field y: {generated}");
    }

    #[test]
    fn token_streams_are_usable_outside_the_compiler() {
        let tokens: TokenStream2 = quote! { let value = 1 + 2; };
        assert_eq!(tokens.to_string(), "let value = 1 + 2 ;");
    }
}
