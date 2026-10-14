//! Procedural macros for this crate.
//!
//! Each `#[proc_macro*]` entry point is a thin shim that converts the
//! compiler's `proc_macro::TokenStream` into a `proc_macro2::TokenStream` and
//! delegates to an `expand_*` function. Those functions only use
//! `proc_macro2`, so they can run (and be unit tested) outside the compiler.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{DeriveInput, parse_macro_input};

/// Derives `fn type_name() -> &'static str` returning the type's identifier.
#[proc_macro_derive(TypeName)]
pub fn derive_type_name(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_type_name(input).into()
}

fn expand_type_name(input: DeriveInput) -> TokenStream2 {
    let ident = &input.ident;
    let name = ident.to_string();
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    quote! {
        impl #impl_generics #ident #ty_generics #where_clause {
            pub fn type_name() -> &'static str {
                #name
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_type_name_impl() {
        let input: DeriveInput = syn::parse_quote! {
            struct Foo<T> { value: T }
        };

        let expected = quote! {
            impl<T> Foo<T> {
                pub fn type_name() -> &'static str {
                    "Foo"
                }
            }
        };

        assert_eq!(expand_type_name(input).to_string(), expected.to_string());
    }
}
