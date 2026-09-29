use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::{quote, ToTokens};
use syn::{
    parse_macro_input, parse_quote,
    visit_mut::{self, VisitMut},
    Data, DeriveInput, Expr, Fields, ItemFn,
};

#[proc_macro_attribute]
pub fn trace(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let func = parse_macro_input!(item as ItemFn);
    instrument(func).into_token_stream().into()
}

#[proc_macro_attribute]
pub fn strip_dbg(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let mut func = parse_macro_input!(item as ItemFn);
    StripDbg.visit_block_mut(&mut func.block);
    func.into_token_stream().into()
}

#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    match describe(&input) {
        Ok(tokens) => tokens.into(),
        Err(err) => err.to_compile_error().into(),
    }
}

fn instrument(mut func: ItemFn) -> ItemFn {
    let name = func.sig.ident.to_string();
    let entry: syn::Stmt = parse_quote! {
        eprintln!("[trace] enter {}", #name);
    };
    func.block.stmts.insert(0, entry);
    func
}

struct StripDbg;

impl VisitMut for StripDbg {
    fn visit_expr_mut(&mut self, expr: &mut Expr) {
        if let Expr::Macro(mac) = expr {
            if mac.mac.path.is_ident("dbg") {
                if let Ok(inner) = mac.mac.parse_body::<Expr>() {
                    *expr = inner;
                    return;
                }
            }
        }
        visit_mut::visit_expr_mut(self, expr);
    }
}

fn describe(input: &DeriveInput) -> syn::Result<TokenStream2> {
    let name = &input.ident;
    let fields = match &input.data {
        Data::Struct(data) => &data.fields,
        _ => {
            return Err(syn::Error::new_spanned(
                input,
                "Describe can only be derived for structs",
            ))
        }
    };

    let names = field_names(fields);
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn field_names() -> &'static [&'static str] {
                &[#(#names),*]
            }
        }
    })
}

fn field_names(fields: &Fields) -> Vec<String> {
    fields
        .iter()
        .enumerate()
        .map(|(index, field)| match &field.ident {
            Some(ident) => ident.to_string(),
            None => index.to_string(),
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn instrument_inserts_entry_statement() {
        let func: ItemFn = parse_quote! {
            fn add(a: i32, b: i32) -> i32 {
                a + b
            }
        };

        let result = instrument(func);
        let tokens = quote!(#result).to_string();

        assert!(tokens.contains("trace"));
        assert!(tokens.contains("add"));
        assert_eq!(result.block.stmts.len(), 2);
    }

    #[test]
    fn strip_dbg_unwraps_inner_expression() {
        let mut func: ItemFn = parse_quote! {
            fn value() -> i32 {
                dbg!(21 * 2)
            }
        };

        StripDbg.visit_block_mut(&mut func.block);
        let tokens = quote!(#func).to_string();

        assert!(!tokens.contains("dbg"));
        assert!(tokens.contains("21"));
    }

    #[test]
    fn field_names_reads_named_fields_in_order() {
        let input: DeriveInput = parse_quote! {
            struct Point {
                x: f64,
                y: f64,
            }
        };

        let Data::Struct(data) = &input.data else {
            panic!("expected struct");
        };

        assert_eq!(field_names(&data.fields), vec!["x", "y"]);
    }

    #[test]
    fn field_names_falls_back_to_indices() {
        let input: DeriveInput = parse_quote! {
            struct Pair(u8, u8);
        };

        let Data::Struct(data) = &input.data else {
            panic!("expected struct");
        };

        assert_eq!(field_names(&data.fields), vec!["0", "1"]);
    }

    #[test]
    fn describe_rejects_non_structs() {
        let input: DeriveInput = parse_quote! {
            enum Color {
                Red,
            }
        };

        assert!(describe(&input).is_err());
    }
}
