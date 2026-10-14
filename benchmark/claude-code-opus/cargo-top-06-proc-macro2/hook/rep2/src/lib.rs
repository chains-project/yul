//! Procedural macros for `my_macros`.
//!
//! Each macro is a thin shim over an implementation written against
//! [`proc_macro2`], which works outside the compiler and can be unit-tested.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{DeriveInput, parse2};

/// Derives `fn type_name() -> &'static str` returning the type's identifier.
#[proc_macro_derive(TypeName)]
pub fn derive_type_name(input: TokenStream) -> TokenStream {
    type_name_impl(input.into()).into()
}

fn type_name_impl(input: TokenStream2) -> TokenStream2 {
    let input: DeriveInput = match parse2(input) {
        Ok(input) => input,
        Err(err) => return err.to_compile_error(),
    };
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
    fn expands_type_name() {
        let input = quote! { struct Foo<T> { x: T } };
        let expected = quote! {
            impl<T> Foo<T> {
                pub fn type_name() -> &'static str {
                    "Foo"
                }
            }
        };
        assert_eq!(type_name_impl(input).to_string(), expected.to_string());
    }

    #[test]
    fn reports_parse_errors() {
        let output = type_name_impl(quote! { not a type }).to_string();
        assert!(output.contains("compile_error"));
    }
}
