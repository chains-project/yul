//! Procedural macros that parse Rust source into a `syn` syntax tree,
//! inspect and transform it, and emit new tokens with `quote`.

use proc_macro::TokenStream;
use quote::quote;
use syn::visit_mut::{self, VisitMut};
use syn::{Expr, ItemFn, LitStr, parse_macro_input};

/// Example attribute macro showing the parse → inspect → transform → emit loop.
///
/// - Inspects the function signature to log its name (or a custom label) on entry.
/// - Transforms the body, rewriting every `a + b` into `(a).wrapping_add(b)`.
#[proc_macro_attribute]
pub fn trace(attr: TokenStream, item: TokenStream) -> TokenStream {
    let label = if attr.is_empty() {
        None
    } else {
        Some(parse_macro_input!(attr as LitStr))
    };
    let mut func = parse_macro_input!(item as ItemFn);

    WrappingAdd.visit_block_mut(&mut func.block);

    let name = label
        .map(|l| l.value())
        .unwrap_or_else(|| func.sig.ident.to_string());
    let body = &func.block;
    func.block = syn::parse_quote!({
        ::std::eprintln!("enter {}", #name);
        #body
    });

    quote!(#func).into()
}

struct WrappingAdd;

impl VisitMut for WrappingAdd {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        // Recurse first so nested additions are rewritten bottom-up.
        visit_mut::visit_expr_mut(self, expr);
        if let Expr::Binary(bin) = expr
            && matches!(bin.op, syn::BinOp::Add(_))
        {
            let (lhs, rhs) = (&bin.left, &bin.right);
            *expr = syn::parse_quote!((#lhs).wrapping_add(#rhs));
        }
    }
}
