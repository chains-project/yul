//! Parse Rust source into a [`syn`] syntax tree, inspect it, and transform it.
//!
//! This crate holds the actual logic so it can be unit-tested like a normal
//! library. The `ast-macros` crate is a thin [`proc-macro`] wrapper around it.

use proc_macro2::TokenStream;
use quote::quote;
use syn::visit_mut::{self, VisitMut};
use syn::{File, Ident, Item};

/// Parse a whole Rust source file into a syntax tree.
pub fn parse_file(source: &str) -> syn::Result<File> {
    syn::parse_file(source)
}

/// Parse a single item (fn, struct, impl, ...) from a token stream.
pub fn parse_item(tokens: TokenStream) -> syn::Result<Item> {
    syn::parse2(tokens)
}

/// Parse any type implementing [`syn::parse::Parse`] from a token stream.
pub fn parse_tokens<T: syn::parse::Parse>(tokens: TokenStream) -> syn::Result<T> {
    syn::parse2(tokens)
}

/// Render a syntax tree back into a token stream.
pub fn to_tokens(item: &Item) -> TokenStream {
    quote!(#item)
}

/// Rename every identifier equal to `from` to `to`, recursively.
pub fn rename_ident(item: &mut Item, from: &str, to: &str) {
    let mut renamer = Renamer {
        from,
        to: Ident::new(to, proc_macro2::Span::call_site()),
    };
    renamer.visit_item_mut(item);
}

struct Renamer<'a> {
    from: &'a str,
    to: Ident,
}

impl VisitMut for Renamer<'_> {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if ident == self.from {
            *ident = self.to.clone();
        }
        visit_mut::visit_ident_mut(self, ident);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_a_source_file() {
        let file = parse_file("fn main() { let x = 1; }").unwrap();
        assert_eq!(file.items.len(), 1);
    }

    #[test]
    fn inspects_and_renames_identifiers() {
        let mut item = parse_item(quote! {
            fn add(old: i32) -> i32 {
                let old = old + 1;
                old
            }
        })
        .unwrap();

        rename_ident(&mut item, "old", "new");

        let rendered = to_tokens(&item).to_string();
        assert!(rendered.contains("new"));
        assert!(!rendered.contains("old"));
    }
}
