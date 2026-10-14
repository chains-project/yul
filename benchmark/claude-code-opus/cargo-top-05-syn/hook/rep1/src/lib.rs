//! Procedural macros that parse Rust source into a `syn` syntax tree,
//! inspect it, and emit transformed code.

use proc_macro::TokenStream;
use quote::quote;
use syn::spanned::Spanned;
use syn::visit_mut::{self, VisitMut};
use syn::{BinOp, Expr, ItemFn, Safety, parse_macro_input, parse_quote};

/// Rewrites integer `+`, `-` and `*` in a function body into checked
/// operations that panic with a descriptive message on overflow.
///
/// ```
/// use my_macros::checked_arith;
///
/// #[checked_arith]
/// fn add(a: u8, b: u8) -> u8 {
///     a + b
/// }
///
/// assert_eq!(add(1, 2), 3);
/// ```
#[proc_macro_attribute]
pub fn checked_arith(args: TokenStream, input: TokenStream) -> TokenStream {
    if !args.is_empty() {
        let args = proc_macro2::TokenStream::from(args);
        return syn::Error::new(args.span(), "#[checked_arith] takes no arguments")
            .into_compile_error()
            .into();
    }

    let mut func = parse_macro_input!(input as ItemFn);

    match expand(&mut func) {
        Ok(()) => quote!(#func).into(),
        Err(err) => err.into_compile_error().into(),
    }
}

fn expand(func: &mut ItemFn) -> syn::Result<()> {
    // Inspect: reject signatures the transform doesn't support.
    if let Safety::Unsafe(token) = &func.sig.safety {
        return Err(syn::Error::new_spanned(
            token,
            "#[checked_arith] does not support unsafe fn",
        ));
    }

    // Transform: walk the body and rewrite arithmetic in place.
    CheckedArith.visit_block_mut(&mut func.block);
    Ok(())
}

struct CheckedArith;

impl VisitMut for CheckedArith {
    fn visit_expr_mut(&mut self, node: &mut Expr) {
        // Recurse first so nested operands are rewritten before their parent.
        visit_mut::visit_expr_mut(self, node);

        let Expr::Binary(bin) = node else { return };
        let method = match bin.op {
            BinOp::Add(_) => quote!(checked_add),
            BinOp::Sub(_) => quote!(checked_sub),
            BinOp::Mul(_) => quote!(checked_mul),
            _ => return,
        };
        let (left, right) = (&bin.left, &bin.right);
        let msg = format!("arithmetic overflow in `{}`", quote!(#bin));
        *node = parse_quote! {
            (#left).#method(#right).expect(#msg)
        };
    }

    // Don't descend into nested closures or items; they are not this
    // function's body and may operate on non-integer types.
    fn visit_expr_closure_mut(&mut self, _: &mut syn::ExprClosure) {}
    fn visit_item_mut(&mut self, _: &mut syn::Item) {}
}
