use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse_macro_input, Fields, ItemStruct};

/// Generates a struct plus a constructor and a getter per field.
///
/// ```ignore
/// make_struct! {
///     pub struct User {
///         pub name: String,
///         pub age: u32,
///     }
/// }
/// ```
///
/// The input is parsed into an AST, then new Rust source is emitted as a
/// `proc_macro2::TokenStream` via `quote!` before being handed back to the
/// compiler.
#[proc_macro]
pub fn make_struct(input: TokenStream) -> TokenStream {
    let item = parse_macro_input!(input as ItemStruct);
    match expand(item) {
        Ok(tokens) => tokens.into(),
        Err(err) => err.to_compile_error().into(),
    }
}

fn expand(item: ItemStruct) -> syn::Result<TokenStream2> {
    let name = &item.ident;
    let vis = &item.vis;

    let fields = match &item.fields {
        Fields::Named(named) => &named.named,
        _ => {
            return Err(syn::Error::new_spanned(
                &item,
                "make_struct! only supports structs with named fields",
            ))
        }
    };

    let field_names: Vec<_> = fields.iter().map(|f| f.ident.clone().unwrap()).collect();
    let field_types: Vec<_> = fields.iter().map(|f| &f.ty).collect();

    let doc = format!("Constructs a new `{name}`.");
    Ok(quote! {
        #item

        impl #name {
            #[doc = #doc]
            #vis fn new(#(#field_names: #field_types),*) -> Self {
                Self { #(#field_names),* }
            }

            #(
                #vis fn #field_names(&self) -> &#field_types {
                    &self.#field_names
                }
            )*
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use syn::parse_quote;

    #[test]
    fn emits_parseable_tokens() {
        let item: ItemStruct = parse_quote! {
            pub struct User {
                pub name: String,
                pub age: u32,
            }
        };

        let tokens = expand(item).expect("expansion should succeed");
        let file: syn::File = syn::parse2(tokens).expect("generated tokens should parse");

        assert_eq!(file.items.len(), 2, "expected a struct and an impl block");
    }

    #[test]
    fn rejects_tuple_structs() {
        let item: ItemStruct = parse_quote! {
            pub struct Point(u32, u32);
        };

        assert!(expand(item).is_err());
    }
}
