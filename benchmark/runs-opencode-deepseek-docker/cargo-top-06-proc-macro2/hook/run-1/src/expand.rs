//! Compiler-independent expansion logic, built on `proc_macro2`.

use proc_macro2::TokenStream;
use quote::quote;
use syn::{DeriveInput, Error};

pub fn derive_hello(input: &DeriveInput) -> Result<TokenStream, Error> {
    let name = &input.ident;
    Ok(quote! {
        impl #name {
            pub fn hello() -> &'static str {
                stringify!(#name)
            }
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use syn::parse_quote;

    #[test]
    fn hello_uses_the_type_name() {
        let input: DeriveInput = parse_quote!(
            struct Foo;
        );
        let expanded = derive_hello(&input).unwrap().to_string();
        assert!(expanded.contains("impl Foo"));
        assert!(expanded.contains("fn hello"));
        assert!(expanded.contains("stringify ! (Foo)"));
    }
}
