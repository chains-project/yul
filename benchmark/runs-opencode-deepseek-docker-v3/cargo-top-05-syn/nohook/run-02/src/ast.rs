//! A thin layer over [`syn`] that turns Rust token streams / source text into a
//! syntax tree which the macros in this crate can inspect and rewrite.
//!
//! The same visitor used for inspection ([`IdentCollector`]) and the one used
//! for transformation ([`RenameIdent`]) are ordinary `syn` `Visit`/`VisitMut`
//! implementations, so they compose with the rest of the `syn` ecosystem.

use std::collections::BTreeSet;

use proc_macro2::TokenStream;
use quote::ToTokens;
use syn::visit::{self, Visit};
use syn::visit_mut::{self, VisitMut};
use syn::{File, Ident, ItemFn};

/// A parsed function kept around so it can be inspected and rewritten.
pub struct Ast {
    item: ItemFn,
}

impl Ast {
    /// Parse a function from the token stream produced by the compiler.
    pub fn parse(tokens: TokenStream) -> syn::Result<Self> {
        Ok(Self::from_item(syn::parse2::<ItemFn>(tokens)?))
    }

    /// Wrap an already parsed [`ItemFn`].
    pub fn from_item(item: ItemFn) -> Self {
        Self { item }
    }

    /// Parse a complete Rust source file into a syntax tree.
    ///
    /// Unlike [`Ast::parse`] this accepts real source text (shebang, inner
    /// attributes, multiple items) exactly as it would appear in a `.rs` file.
    pub fn parse_source(source: &str) -> syn::Result<File> {
        syn::parse_file(source)
    }

    /// The name of the annotated function.
    pub fn function_name(&self) -> &Ident {
        &self.item.sig.ident
    }

    /// Every identifier referenced anywhere in the function, deduplicated and
    /// sorted.
    pub fn identifiers(&self) -> BTreeSet<String> {
        collect_identifiers(|visitor| visitor.visit_item_fn(&self.item))
    }

    /// Rename every occurrence of the identifier `from` to `to`.
    ///
    /// Returns the number of identifiers that were rewritten. Both names are
    /// validated as legal Rust identifiers before any rewriting happens.
    pub fn rename(&mut self, from: &str, to: &str) -> syn::Result<usize> {
        let from = parse_ident(from)?;
        let to = parse_ident(to)?;

        let mut renamer = RenameIdent { from, to, count: 0 };
        renamer.visit_item_fn_mut(&mut self.item);
        Ok(renamer.count)
    }

    /// Emit the (possibly transformed) function back as a token stream.
    pub fn into_token_stream(self) -> TokenStream {
        self.item.into_token_stream()
    }
}

/// Collect the identifiers used in a parsed source file.
pub fn identifiers_in_file(file: &File) -> BTreeSet<String> {
    collect_identifiers(|visitor| visitor.visit_file(file))
}

/// Run a [`Visit`]-based collection over any part of the tree.
fn collect_identifiers(run: impl FnOnce(&mut IdentCollector)) -> BTreeSet<String> {
    let mut collector = IdentCollector::default();
    run(&mut collector);
    collector.found
}

/// Parse `name`, rejecting anything that is not a legal identifier (including
/// reserved keywords such as `fn` or `let`).
fn parse_ident(name: &str) -> syn::Result<Ident> {
    syn::parse_str::<Ident>(name)
}

/// Inspects a tree and records every identifier it encounters.
#[derive(Default)]
struct IdentCollector {
    found: BTreeSet<String>,
}

impl<'ast> Visit<'ast> for IdentCollector {
    fn visit_ident(&mut self, ident: &'ast Ident) {
        self.found.insert(ident.to_string());
        visit::visit_ident(self, ident);
    }
}

/// Rewrites every identifier matching `from` into `to`.
struct RenameIdent {
    from: Ident,
    to: Ident,
    count: usize,
}

impl VisitMut for RenameIdent {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if *ident == self.from {
            *ident = self.to.clone();
            self.count += 1;
        }
        visit_mut::visit_ident_mut(self, ident);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn parses_a_function() {
        let ast = Ast::parse(quote!(
            fn answer() -> i32 {
                42
            }
        ))
        .unwrap();
        assert_eq!(ast.function_name(), "answer");
    }

    #[test]
    fn inspects_identifiers() {
        let ast = Ast::parse(quote!(
            fn area(w: i32, h: i32) -> i32 {
                w * h
            }
        ))
        .unwrap();
        let idents = ast.identifiers();
        assert!(idents.contains("area"));
        assert!(idents.contains("w"));
        assert!(idents.contains("h"));
        assert!(idents.contains("i32"));
    }

    #[test]
    fn transforms_identifiers() {
        let mut ast = Ast::parse(quote!(
            fn f() {
                let width = 1;
                let _ = width;
            }
        ))
        .unwrap();
        let count = ast.rename("width", "height").unwrap();
        assert_eq!(count, 2);

        let output = ast.into_token_stream().to_string();
        assert!(output.contains("height"));
        assert!(!output.contains("width"));
    }

    #[test]
    fn parses_source_text() {
        let file = Ast::parse_source("pub fn one() -> u8 { 1 }\nfn two() {}\n").unwrap();
        assert_eq!(file.items.len(), 2);

        let idents = identifiers_in_file(&file);
        assert!(idents.contains("one"));
        assert!(idents.contains("two"));
        assert!(idents.contains("u8"));
    }

    #[test]
    fn rejects_invalid_identifiers() {
        let mut ast = Ast::parse(quote!(
            fn f() {}
        ))
        .unwrap();
        assert!(ast.rename("f", "fn").is_err());
        assert!(ast.rename("not an ident", "x").is_err());
    }
}
