//! Procedural macros for this crate.
//!
//! The `#[proc_macro*]` entry points are thin shims: they convert the
//! compiler's `proc_macro::TokenStream` into `proc_macro2::TokenStream` and
//! delegate to plain functions. Those functions use only `proc_macro2`, so they
//! can be unit-tested and reused outside of a compiler-invoked macro context.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{DeriveInput, parse2};

/// Example derive: `#[derive(Hello)]` adds `fn hello() -> &'static str`.
#[proc_macro_derive(Hello)]
pub fn derive_hello(input: TokenStream) -> TokenStream {
    expand_hello(input.into()).into()
}

fn expand_hello(input: TokenStream2) -> TokenStream2 {
    let input: DeriveInput = match parse2(input) {
        Ok(input) => input,
        Err(err) => return err.to_compile_error(),
    };
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();
    let message = format!("Hello from {name}!");

    quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn hello() -> &'static str {
                #message
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_outside_compiler() {
        let out = expand_hello(quote! { struct Foo; });
        let expected = quote! {
            impl Foo {
                pub fn hello() -> &'static str {
                    "Hello from Foo!"
                }
            }
        };
        assert_eq!(out.to_string(), expected.to_string());
    }

    #[test]
    fn reports_parse_errors() {
        let out = expand_hello(quote! { fn not_a_type() {} });
        assert!(out.to_string().contains("compile_error"));
    }
}
