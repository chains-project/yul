//! Procedural macros for this project.
//!
//! Each macro entry point is a thin shim that converts between the compiler's
//! `proc_macro::TokenStream` and `proc_macro2::TokenStream`. All real logic
//! lives in functions operating on `proc_macro2` types, so it can be unit
//! tested without a compiler-driven macro invocation.

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{DeriveInput, parse_macro_input};

/// Derives a `hello()` associated function that returns the type's name.
#[proc_macro_derive(Hello)]
pub fn derive_hello(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_hello(input).into()
}

fn expand_hello(input: DeriveInput) -> TokenStream2 {
    let name = &input.ident;
    let name_str = name.to_string();
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn hello() -> &'static str {
                #name_str
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_outside_the_compiler() {
        let input: DeriveInput = syn::parse2(quote! { struct Foo<T>(T); }).unwrap();
        let output = expand_hello(input).to_string();
        assert!(output.contains("impl < T > Foo < T >"), "{output}");
        assert!(output.contains("\"Foo\""), "{output}");
    }
}
