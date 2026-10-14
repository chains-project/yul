//! Procedural macros.

use proc_macro::TokenStream;
use quote::quote;
use syn::visit_mut::{self, VisitMut};
use syn::{BinOp, Expr, ItemFn, parse_macro_input, parse_quote};

/// Rewrites every `a + b` in the annotated function body into `a.wrapping_add(b)`.
///
/// A starter example of the parse → inspect/transform → re-emit pipeline.
#[proc_macro_attribute]
pub fn wrapping_add(attr: TokenStream, item: TokenStream) -> TokenStream {
    if !attr.is_empty() {
        let attr = proc_macro2::TokenStream::from(attr);
        return syn::Error::new_spanned(attr, "`#[wrapping_add]` takes no arguments")
            .to_compile_error()
            .into();
    }

    let mut func = parse_macro_input!(item as ItemFn);
    WrappingAdd.visit_item_fn_mut(&mut func);
    quote!(#func).into()
}

struct WrappingAdd;

impl VisitMut for WrappingAdd {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        // Transform children first so nested additions are rewritten too.
        visit_mut::visit_expr_mut(self, expr);

        if let Expr::Binary(bin) = expr
            && let BinOp::Add(_) = bin.op
        {
            let (left, right) = (&bin.left, &bin.right);
            *expr = parse_quote!((#left).wrapping_add(#right));
        }
    }
}
