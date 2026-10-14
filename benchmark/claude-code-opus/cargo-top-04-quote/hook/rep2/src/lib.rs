//! Procedural macros.
//!
//! The usual split: `syn` parses the input `TokenStream` into a syntax tree,
//! `quote!` builds the output Rust code, and `proc_macro2` provides the token
//! types used in between (they work outside the compiler, so they're testable).

use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{DeriveInput, parse_macro_input};

/// Derives `fn type_name() -> &'static str` returning the type's identifier.
///
/// ```
/// use my_macros::TypeName;
///
/// #[derive(TypeName)]
/// struct Point;
///
/// assert_eq!(Point::type_name(), "Point");
/// ```
#[proc_macro_derive(TypeName)]
pub fn derive_type_name(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand_type_name(&input).into()
}

fn expand_type_name(input: &DeriveInput) -> TokenStream2 {
    let name = &input.ident;
    let name_str = name.to_string();
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn type_name() -> &'static str {
                #name_str
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn expands_impl_with_generics() {
        let input: DeriveInput = syn::parse_quote! {
            struct Wrapper<T: Clone> where T: Send { value: T }
        };
        let expected = quote! {
            impl<T: Clone> Wrapper<T> where T: Send {
                pub fn type_name() -> &'static str {
                    "Wrapper"
                }
            }
        };
        assert_eq!(expand_type_name(&input).to_string(), expected.to_string());
    }
}
