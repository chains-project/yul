use proc_macro2::TokenStream;
use quote::ToTokens;
use syn::visit_mut::{self, VisitMut};
use syn::{BinOp, Expr, ExprBinary, Item, ItemFn, parse_quote};

pub fn expand(args: TokenStream, mut item: ItemFn) -> syn::Result<TokenStream> {
    if !args.is_empty() {
        return Err(syn::Error::new_spanned(
            args,
            "#[checked_arith] does not take arguments",
        ));
    }
    CheckedArith.visit_block_mut(&mut item.block);
    Ok(item.into_token_stream())
}

struct CheckedArith;

impl VisitMut for CheckedArith {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        // Rewrite children first so nested operations are handled bottom-up.
        visit_mut::visit_expr_mut(self, expr);

        if let Expr::Binary(ExprBinary {
            left, op, right, ..
        }) = expr
        {
            let (method, msg) = match op {
                BinOp::Add(_) => (
                    quote::format_ident!("checked_add"),
                    "attempt to add with overflow",
                ),
                BinOp::Sub(_) => (
                    quote::format_ident!("checked_sub"),
                    "attempt to subtract with overflow",
                ),
                BinOp::Mul(_) => (
                    quote::format_ident!("checked_mul"),
                    "attempt to multiply with overflow",
                ),
                _ => return,
            };
            *expr = parse_quote!((#left).#method(#right).expect(#msg));
        }
    }

    // Nested items (inner fns, impls, ...) are separate scopes; leave them alone.
    fn visit_item_mut(&mut self, _item: &mut Item) {}
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::quote;

    #[test]
    fn rewrites_nested_arithmetic() {
        let item: ItemFn = parse_quote! {
            fn f(a: u32, b: u32, c: u32) -> u32 { a + b * c - 1 }
        };
        let expected: ItemFn = parse_quote! {
            fn f(a: u32, b: u32, c: u32) -> u32 {
                ((a).checked_add((b).checked_mul(c).expect("attempt to multiply with overflow"))
                    .expect("attempt to add with overflow"))
                    .checked_sub(1)
                    .expect("attempt to subtract with overflow")
            }
        };
        let out: ItemFn = syn::parse2(expand(TokenStream::new(), item).unwrap()).unwrap();
        assert_eq!(out, expected);
    }

    #[test]
    fn leaves_other_operators_and_nested_items_alone() {
        let item: ItemFn = parse_quote! {
            fn f(a: u32) -> bool {
                fn inner(x: u32) -> u32 { x + 1 }
                a / 2 == inner(a)
            }
        };
        let out: ItemFn = syn::parse2(expand(TokenStream::new(), item.clone()).unwrap()).unwrap();
        assert_eq!(out, item);
    }

    #[test]
    fn rejects_arguments() {
        let item: ItemFn = parse_quote! { fn f() {} };
        let err = expand(quote!(foo), item).unwrap_err();
        assert!(err.to_string().contains("does not take arguments"));
    }
}
