use proc_macro2::TokenStream;
use quote::quote;
use syn::{parse_quote, ItemFn};

/// Shared code-generation logic, kept independent of the `proc_macro` runtime
/// so it can be unit tested with `proc_macro2` token streams.
pub fn make_answer_fn() -> ItemFn {
    parse_quote! {
        fn answer() -> u32 {
            42
        }
    }
}

pub fn make_answer() -> TokenStream {
    let item = make_answer_fn();
    quote!(#item)
}

pub fn const_ident_function(name: &syn::Ident, value: u32) -> TokenStream {
    quote! {
        fn #name() -> u32 {
            #value
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn generates_answer_function() {
        let generated = make_answer();
        assert_eq!(generated.to_string(), quote!(fn answer() -> u32 { 42 }).to_string());
    }

    #[test]
    fn generates_named_const_function() {
        let name = syn::Ident::new("meaning", proc_macro2::Span::call_site());
        let generated = const_ident_function(&name, 42);
        assert_eq!(
            generated.to_string(),
            quote!(fn meaning() -> u32 { 42u32 }).to_string()
        );
    }
}
