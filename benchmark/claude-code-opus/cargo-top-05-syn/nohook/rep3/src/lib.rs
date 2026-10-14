//! Procedural macros built on `syn` (parsing), `quote` (code generation),
//! and `proc-macro2` (token types usable outside the compiler, e.g. in tests).

use proc_macro::TokenStream;
use quote::quote;
use syn::visit_mut::{self, VisitMut};
use syn::{BinOp, Expr, ItemFn, parse_macro_input, parse_quote};

/// Rewrites `+`, `-` and `*` in the annotated function body into
/// `saturating_add`, `saturating_sub` and `saturating_mul` calls.
///
/// ```
/// #[macros::saturating]
/// fn add(a: u8, b: u8) -> u8 {
///     a + b
/// }
///
/// assert_eq!(add(200, 100), u8::MAX);
/// ```
#[proc_macro_attribute]
pub fn saturating(args: TokenStream, input: TokenStream) -> TokenStream {
    if !args.is_empty() {
        let args = proc_macro2::TokenStream::from(args);
        return syn::Error::new_spanned(args, "#[saturating] takes no arguments")
            .to_compile_error()
            .into();
    }

    let mut func = parse_macro_input!(input as ItemFn);
    Saturating.visit_item_fn_mut(&mut func);
    quote!(#func).into()
}

struct Saturating;

impl VisitMut for Saturating {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        // Transform children first so nested expressions are rewritten too.
        visit_mut::visit_expr_mut(self, expr);

        if let Expr::Binary(bin) = expr {
            let method = match bin.op {
                BinOp::Add(_) => quote!(saturating_add),
                BinOp::Sub(_) => quote!(saturating_sub),
                BinOp::Mul(_) => quote!(saturating_mul),
                _ => return,
            };
            let (left, right) = (&bin.left, &bin.right);
            *expr = parse_quote!((#left).#method(#right));
        }
    }
}
