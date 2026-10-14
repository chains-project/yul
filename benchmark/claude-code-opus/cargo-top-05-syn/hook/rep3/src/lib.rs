//! Procedural macros that parse Rust source into a `syn` syntax tree,
//! inspect it, and emit transformed code.

use proc_macro::TokenStream;
use quote::quote;
use syn::visit_mut::{self, VisitMut};
use syn::{BinOp, Expr, ItemFn, parse_macro_input, parse_quote};

/// Rewrites `a + b`, `a - b` and `a * b` inside the annotated function into
/// `checked_*` calls that panic with a descriptive message on overflow,
/// regardless of build profile.
///
/// ```
/// #[my_macros::checked_arith]
/// fn add(a: u8, b: u8) -> u8 {
///     a + b
/// }
///
/// assert_eq!(add(1, 2), 3);
/// assert!(std::panic::catch_unwind(|| add(255, 1)).is_err());
/// ```
#[proc_macro_attribute]
pub fn checked_arith(attr: TokenStream, item: TokenStream) -> TokenStream {
    if !attr.is_empty() {
        let attr = proc_macro2::TokenStream::from(attr);
        return syn::Error::new_spanned(attr, "#[checked_arith] takes no arguments")
            .into_compile_error()
            .into();
    }

    let mut func = parse_macro_input!(item as ItemFn);
    let fn_name = func.sig.ident.to_string();
    CheckedArith { fn_name }.visit_block_mut(&mut func.block);

    quote!(#func).into()
}

struct CheckedArith {
    fn_name: String,
}

impl VisitMut for CheckedArith {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        // Recurse first so nested operands are rewritten bottom-up.
        visit_mut::visit_expr_mut(self, expr);

        let Expr::Binary(bin) = expr else { return };
        let method = match bin.op {
            BinOp::Add(_) => "checked_add",
            BinOp::Sub(_) => "checked_sub",
            BinOp::Mul(_) => "checked_mul",
            _ => return,
        };
        let method = syn::Ident::new(method, proc_macro2::Span::call_site());
        let (left, right) = (&bin.left, &bin.right);
        let msg = format!("arithmetic overflow in `{}`", self.fn_name);
        // Binding through an array unifies both operand types before the method
        // call, so `2 * x` works even though `2` alone is an untyped literal.
        *expr = parse_quote! {
            {
                let [__lhs, __rhs] = [#left, #right];
                __lhs.#method(__rhs).expect(#msg)
            }
        };
    }
}
