//! Procedural macros that parse, inspect, and transform Rust syntax trees.

use proc_macro::TokenStream;
use quote::quote;
use syn::parse::{Parse, ParseStream};
use syn::parse_macro_input;
use syn::{Ident, Item, Token};

struct RenameArgs {
    from: Ident,
    to: Ident,
}

impl Parse for RenameArgs {
    fn parse(input: ParseStream<'_>) -> syn::Result<Self> {
        let from = input.parse()?;
        input.parse::<Token![,]>()?;
        let to = input.parse()?;
        Ok(Self { from, to })
    }
}

/// Parse the annotated item, rename identifiers, and emit the result.
///
/// ```ignore
/// #[ast_rename(old_name, new_name)]
/// fn demo() {
///     let old_name = 1;
/// }
/// ```
#[proc_macro_attribute]
pub fn ast_rename(attr: TokenStream, item: TokenStream) -> TokenStream {
    let args = parse_macro_input!(attr as RenameArgs);
    let mut ast = parse_macro_input!(item as Item);

    ast_core::rename_ident(&mut ast, &args.from.to_string(), &args.to.to_string());

    quote!(#ast).into()
}
