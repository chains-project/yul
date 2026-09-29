//! A procedural-macro crate that parses Rust source into a [`syn`] syntax tree,
//! walks the tree to inspect it, and writes a transformed tree back out.
//!
//! The crate is built around three steps:
//!
//! 1. **Parse** — [`syn::parse_macro_input!`] turns the macro's incoming token
//!    stream into typed `syn` nodes, and [`syn::parse_str`] parses ordinary
//!    source text into the same tree (useful for tests and tooling).
//! 2. **Inspect** — the [`syn::visit_mut::VisitMut`] trait walks every node of
//!    the tree and lets a visitor decide which nodes to look at.
//! 3. **Transform / emit** — mutated nodes are rendered back to a token stream
//!    with [`quote::quote!`].
//!
//! The [`rename`] attribute macro ties the three steps together: it parses the
//! annotated item, renames an identifier throughout the tree, and emits the
//! transformed item.

use proc_macro::TokenStream;
use quote::quote;
use syn::parse::{Parse, ParseStream};
use syn::visit_mut::VisitMut;
use syn::{parse_macro_input, Ident, Item, Token};

/// Renames every occurrence of one identifier to another inside the annotated
/// item.
///
/// The macro is a compact demonstration of the parse/inspect/transform
/// pipeline: `attr` is parsed into [`RenameArgs`], the item is parsed into a
/// [`syn::Item`], a [`Renamer`] visitor walks the tree, and the result is
/// emitted with [`quote!`].
///
/// # Examples
///
/// ```ignore
/// #[rename(foo, bar)]
/// fn demo() {
///     let foo = 1;
///     let _ = foo; // becomes `bar`
/// }
/// ```
#[proc_macro_attribute]
pub fn rename(attr: TokenStream, item: TokenStream) -> TokenStream {
    let args = parse_macro_input!(attr as RenameArgs);
    let mut item = parse_macro_input!(item as Item);

    rename_item(&mut item, &args.from, &args.to);

    quote!(#item).into()
}

/// Applies [`Renamer`] to an already-parsed item.
///
/// Kept separate from the macro entry point so it can be exercised directly
/// against source strings in unit tests.
fn rename_item(item: &mut Item, from: &Ident, to: &Ident) {
    Renamer { from, to }.visit_item_mut(item);
}

/// Arguments accepted by the [`rename`] attribute: `rename(from, to)`.
struct RenameArgs {
    from: Ident,
    to: Ident,
}

impl Parse for RenameArgs {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let from = input.parse()?;
        input.parse::<Token![,]>()?;
        let to = input.parse()?;
        Ok(Self { from, to })
    }
}

/// A [`VisitMut`] visitor that rewrites matching identifiers as it walks.
///
/// Note that `syn` treats macro-invocation bodies (everything between the
/// parens of `some_macro!(...)`) as an opaque token stream, so identifiers
/// inside a nested macro call are not visited. Descending into them would
/// require parsing the tokens with [`syn::parse2`] yourself.
struct Renamer<'a> {
    from: &'a Ident,
    to: &'a Ident,
}

impl VisitMut for Renamer<'_> {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if *ident == *self.from {
            *ident = self.to.clone();
        }
        syn::visit_mut::visit_ident_mut(self, ident);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ident(name: &str) -> Ident {
        Ident::new(name, proc_macro2::Span::call_site())
    }

    fn parse_item(source: &str) -> Item {
        syn::parse_str(source).expect("test source should parse")
    }

    #[test]
    fn renames_every_occurrence() {
        let mut item = parse_item("fn demo() { let foo = 1; let _ = foo; }");

        rename_item(&mut item, &ident("foo"), &ident("bar"));

        let rendered = quote!(#item).to_string();
        assert_eq!(rendered.matches("bar").count(), 2, "{rendered}");
        assert!(!rendered.contains("foo"), "{rendered}");
    }

    #[test]
    fn leaves_unrelated_identifiers_untouched() {
        let mut item = parse_item("fn foo() -> usize { 1 }");

        rename_item(&mut item, &ident("missing"), &ident("found"));

        let rendered = quote!(#item).to_string();
        assert!(rendered.contains("foo"), "{rendered}");
        assert!(!rendered.contains("found"), "{rendered}");
    }
}
