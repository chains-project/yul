//! Procedural macros that generate Rust source as token streams.

use proc_macro::TokenStream;
use quote::quote;
use syn::{DeriveInput, parse_macro_input};

/// Derives a `describe()` associated function returning the type's name.
///
/// ```
/// use codegen_macros::Describe;
///
/// #[derive(Describe)]
/// struct Point;
///
/// assert_eq!(Point::describe(), "Point");
/// ```
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_describe(&input).into()
}

fn expand_describe(input: &DeriveInput) -> proc_macro2::TokenStream {
    let name = &input.ident;
    let name_str = name.to_string();
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn describe() -> &'static str {
                #name_str
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_describe_impl() {
        let input: DeriveInput = syn::parse_quote! { struct Foo<T>(T); };
        let expected = quote! {
            impl<T> Foo<T> {
                pub fn describe() -> &'static str {
                    "Foo"
                }
            }
        };
        assert_eq!(expand_describe(&input).to_string(), expected.to_string());
    }
}
