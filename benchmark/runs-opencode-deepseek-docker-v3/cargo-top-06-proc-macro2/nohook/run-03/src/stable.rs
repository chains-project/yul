use proc_macro2::{TokenStream, TokenTree};
use quote::quote;
use syn::{DeriveInput, parse2};

pub(crate) fn token_count(tokens: TokenStream) -> usize {
    tokens
        .into_iter()
        .map(|tree| match tree {
            TokenTree::Group(group) => 1 + token_count(group.stream()),
            _ => 1,
        })
        .sum()
}

pub(crate) fn render(tokens: &TokenStream) -> String {
    tokens.to_string()
}

pub(crate) fn count_tokens(input: TokenStream) -> TokenStream {
    let count = token_count(input);
    quote!(#count)
}

pub(crate) fn tokens_as_str(input: TokenStream) -> TokenStream {
    let rendered = render(&input);
    quote!(#rendered)
}

pub(crate) fn derive_token_count(input: TokenStream) -> TokenStream {
    let count = token_count(input.clone());
    let parsed: DeriveInput = match parse2(input) {
        Ok(parsed) => parsed,
        Err(err) => return err.to_compile_error(),
    };

    let ident = &parsed.ident;
    let (impl_generics, ty_generics, where_clause) = parsed.generics.split_for_impl();

    quote! {
        impl #impl_generics #ident #ty_generics #where_clause {
            pub const TOKEN_COUNT: usize = #count;
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::str::FromStr;

    fn ts(source: &str) -> TokenStream {
        TokenStream::from_str(source).unwrap()
    }

    #[test]
    fn counts_flat_and_nested_tokens() {
        assert_eq!(token_count(ts("a + b")), 3);
        assert_eq!(token_count(ts("(a + b) * c")), 6);
    }

    #[test]
    fn macro_emits_literal_count() {
        let out = count_tokens(ts("a + b"));
        let lit: syn::LitInt = parse2(out).unwrap();
        assert_eq!(lit.base10_parse::<usize>().unwrap(), 3);
    }

    #[test]
    fn macro_emits_string_literal() {
        let out = tokens_as_str(ts("a + b"));
        let lit: syn::LitStr = parse2(out).unwrap();
        let value = lit.value();
        let words: Vec<&str> = value.split_whitespace().collect();
        assert_eq!(words, ["a", "+", "b"]);
    }

    #[test]
    fn derive_emits_inherent_const() {
        let out = derive_token_count(ts("struct Foo;"));
        let item: syn::ItemImpl = parse2(out).unwrap();
        assert!(item.trait_.is_none());
        assert!(quote!(#item).to_string().contains("TOKEN_COUNT"));
        assert!(quote!(#item).to_string().contains("usize"));
    }

    #[test]
    fn derive_reports_syntax_errors() {
        let out = derive_token_count(ts("not an item"));
        assert!(out.to_string().contains("compile_error"));
    }
}
