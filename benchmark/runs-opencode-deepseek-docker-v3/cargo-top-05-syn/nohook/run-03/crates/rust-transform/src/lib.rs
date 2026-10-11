//! Parsing and AST manipulation for the `rust-transform-macro` crate.
//!
//! All of the `syn` work lives here rather than in the proc-macro crate so
//! that it can be unit tested directly: proc-macro crates can only export
//! macro entry points, they cannot expose ordinary functions to tests.
//!
//! The general pipeline is:
//!
//! 1. [`parse_file`] / [`parse_item_fn`] turn source text into a `syn` tree.
//! 2. An inspector (e.g. [`collect_fn_names`]) or a [`VisitMut`] transform
//!    (e.g. [`double_int_literals_file`]) walks that tree.
//! 3. [`to_token_stream`] renders the tree back to tokens for codegen.

use proc_macro2::TokenStream;
use quote::ToTokens;
use syn::visit::{self, Visit};
use syn::visit_mut::{self, VisitMut};
use syn::{Expr, ExprLit, File, ItemFn, Lit, LitInt};

/// Parse a complete Rust source file into a `syn` syntax tree.
pub fn parse_file(source: &str) -> syn::Result<File> {
    syn::parse_file(source)
}

/// Parse a single function definition from a string.
pub fn parse_item_fn(source: &str) -> syn::Result<ItemFn> {
    syn::parse_str(source)
}

/// Render a syntax tree back into a token stream.
pub fn to_token_stream<T: ToTokens>(node: &T) -> TokenStream {
    node.to_token_stream()
}

/// Rewrites every decimal integer literal by doubling its value.
///
/// Type suffixes are preserved (`21u8` becomes `42u8`) and the replacement
/// keeps the original span, so diagnostics point at the original source.
#[derive(Default)]
pub struct DoubleIntLiterals;

impl VisitMut for DoubleIntLiterals {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        if let Expr::Lit(ExprLit { lit, .. }) = expr {
            if let Lit::Int(int) = lit {
                if let Some(doubled) = double_int(int) {
                    *lit = Lit::Int(doubled);
                    return;
                }
            }
        }
        visit_mut::visit_expr_mut(self, expr);
    }
}

fn double_int(int: &LitInt) -> Option<LitInt> {
    let value = int.base10_parse::<i128>().ok()?;
    let doubled = value.checked_mul(2)?;
    Some(LitInt::new(
        &format!("{doubled}{}", int.suffix()),
        int.span(),
    ))
}

/// Apply [`DoubleIntLiterals`] to every expression in a file.
pub fn double_int_literals_file(file: &mut File) {
    DoubleIntLiterals.visit_file_mut(file);
}

/// Apply [`DoubleIntLiterals`] to a single function.
pub fn double_int_literals_item_fn(item: &mut ItemFn) {
    DoubleIntLiterals.visit_item_fn_mut(item);
}

/// Collects the name of every `fn` item encountered while walking a tree.
#[derive(Default)]
pub struct FnCollector {
    pub names: Vec<String>,
}

impl<'ast> Visit<'ast> for FnCollector {
    fn visit_item_fn(&mut self, node: &'ast ItemFn) {
        self.names.push(node.sig.ident.to_string());
        visit::visit_item_fn(self, node);
    }
}

/// Return the names of all functions defined in `file`, in source order.
pub fn collect_fn_names(file: &File) -> Vec<String> {
    let mut collector = FnCollector::default();
    collector.visit_file(file);
    collector.names
}

/// Collects the value of every integer literal encountered while walking.
#[derive(Default)]
pub struct IntCollector {
    pub values: Vec<i128>,
}

impl<'ast> Visit<'ast> for IntCollector {
    fn visit_lit_int(&mut self, node: &'ast LitInt) {
        if let Ok(value) = node.base10_parse::<i128>() {
            self.values.push(value);
        }
    }
}

/// Return the values of all integer literals in `file`, in source order.
pub fn collect_int_literals(file: &File) -> Vec<i128> {
    let mut collector = IntCollector::default();
    collector.visit_file(file);
    collector.values
}

#[cfg(test)]
mod tests {
    use super::*;

    const SOURCE: &str = r#"
        fn one() -> i32 { 1 }
        fn two() -> i32 { 2u8 }
    "#;

    #[test]
    fn parses_and_inspects() {
        let file = parse_file(SOURCE).expect("valid source");
        assert_eq!(collect_fn_names(&file), ["one", "two"]);
        assert_eq!(collect_int_literals(&file), [1, 2]);
    }

    #[test]
    fn transforms_int_literals() {
        let mut file = parse_file(SOURCE).expect("valid source");
        double_int_literals_file(&mut file);
        assert_eq!(collect_int_literals(&file), [2, 4]);
    }

    #[test]
    fn preserves_suffixes_and_spans() {
        let mut item = parse_item_fn("fn f() -> u8 { 21u8 }").expect("valid fn");
        double_int_literals_item_fn(&mut item);
        let rendered = to_token_stream(&item).to_string();
        assert!(rendered.contains("42u8"), "got: {rendered}");
    }

    #[test]
    fn parses_nested_functions() {
        let file = parse_file("fn outer() { fn inner() {} }").expect("valid source");
        assert_eq!(collect_fn_names(&file), ["outer", "inner"]);
    }
}
