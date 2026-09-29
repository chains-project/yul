//! Example procedural macros that parse Rust source into a [`syn`] syntax
//! tree, inspect it, and rewrite it.
//!
//! Two worked examples are provided:
//!
//! * [`macro@trace`] parses an annotated function as a [`syn::ItemFn`], reads
//!   its name/arity/async-ness from the [`syn::Signature`], and rewrites the
//!   function body.
//! * [`macro@rename_ident`] parses an annotated function and mutates every
//!   matching [`syn::Ident`] in place through
//!   [`syn::visit_mut::VisitMut`].
//!
//! For source that is not already a token stream (e.g. reading a `.rs` file),
//! parse it with [`syn::parse_file`] or `syn::parse_str::<syn::File>`, which
//! both produce a [`syn::File`] root node.

use proc_macro::TokenStream;
use quote::quote;
use syn::parse::{Parse, ParseStream};
use syn::visit_mut::VisitMut;
use syn::{parse_macro_input, parse_quote, Ident, ItemFn, Token};

/// Log every entry into the annotated function.
///
/// The body is parsed into an AST, the signature is inspected, and the body is
/// replaced with a new block that logs before delegating to the original code.
///
/// ```ignore
/// #[rust_ast_tools::trace]
/// fn add(a: i32, b: i32) -> i32 {
///     a + b
/// }
/// ```
#[proc_macro_attribute]
pub fn trace(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let mut func = parse_macro_input!(item as ItemFn);

    let name = func.sig.ident.to_string();
    let arity = func.sig.inputs.len();
    let is_async = func.sig.asyncness.is_some();
    let message = format!("enter `{name}` ({arity} arg(s), async = {is_async})");

    let original_body = (*func.block).clone();
    func.block = Box::new(parse_quote!({
        eprintln!(#message);
        #original_body
    }));

    quote!(#func).into()
}

/// Arguments of [`macro@rename_ident`]: `from -> to`.
struct RenameArgs {
    from: Ident,
    to: Ident,
}

impl Parse for RenameArgs {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let from: Ident = input.parse()?;
        input.parse::<Token![->]>()?;
        let to: Ident = input.parse()?;
        Ok(Self { from, to })
    }
}

/// A [`VisitMut`] pass that swaps one identifier for another.
struct RenameVisitor {
    from: Ident,
    to: Ident,
}

impl VisitMut for RenameVisitor {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if *ident == self.from {
            *ident = self.to.clone();
        }
    }
}

/// Rename every occurrence of `from` to `to` inside the annotated function.
///
/// ```ignore
/// #[rust_ast_tools::rename_ident(old -> new)]
/// fn f() -> i32 {
///     let old = 1;
///     old + 1
/// }
/// ```
#[proc_macro_attribute]
pub fn rename_ident(attr: TokenStream, item: TokenStream) -> TokenStream {
    let args = parse_macro_input!(attr as RenameArgs);
    let mut func = parse_macro_input!(item as ItemFn);

    rename(&mut func, &args.from, &args.to);

    quote!(#func).into()
}

fn rename(func: &mut ItemFn, from: &Ident, to: &Ident) {
    RenameVisitor {
        from: from.clone(),
        to: to.clone(),
    }
    .visit_item_fn_mut(func);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renames_every_matching_identifier() {
        let mut func: ItemFn =
            syn::parse_str("fn f() { let from = 1; let same = from; }").unwrap();
        let from = Ident::new("from", proc_macro2::Span::call_site());
        let to = Ident::new("renamed", proc_macro2::Span::call_site());

        rename(&mut func, &from, &to);

        let printed = quote!(#func).to_string();
        assert!(printed.contains("let renamed = 1"));
        assert!(printed.contains("let same = renamed"));
        assert!(!printed.contains("from"));
    }

    #[test]
    fn parses_a_whole_file_into_a_syntax_tree() {
        let file: syn::File = syn::parse_str(
            "pub struct Point { x: i32, y: i32 }\nfn origin() -> Point { Point { x: 0, y: 0 } }",
        )
        .unwrap();

        assert_eq!(file.items.len(), 2);
    }
}
