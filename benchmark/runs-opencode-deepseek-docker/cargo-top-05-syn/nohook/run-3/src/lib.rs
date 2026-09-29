use proc_macro::TokenStream;
use quote::quote;
use syn::fold::Fold;
use syn::parse::{Parse, ParseStream};
use syn::{parse_macro_input, File, Ident, Item, Token};

#[proc_macro]
pub fn inspect(input: TokenStream) -> TokenStream {
    let file = parse_macro_input!(input as File);
    let names = file
        .items
        .iter()
        .filter_map(item_ident)
        .map(Ident::to_string)
        .collect::<Vec<_>>()
        .join(", ");
    quote!(#names).into()
}

struct TransformInput {
    from: Ident,
    to: Ident,
    file: File,
}

impl Parse for TransformInput {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let from = input.parse()?;
        input.parse::<Token![=>]>()?;
        let to = input.parse()?;
        if input.peek(Token![,]) {
            input.parse::<Token![,]>()?;
        }
        let file = input.parse()?;
        Ok(TransformInput { from, to, file })
    }
}

struct Rename {
    from: Ident,
    to: Ident,
}

impl Fold for Rename {
    fn fold_ident(&mut self, ident: Ident) -> Ident {
        if ident == self.from {
            Ident::new(&self.to.to_string(), ident.span())
        } else {
            ident
        }
    }
}

#[proc_macro]
pub fn transform(input: TokenStream) -> TokenStream {
    let TransformInput { from, to, file } = parse_macro_input!(input as TransformInput);
    let file = Rename { from, to }.fold_file(file);
    quote!(#file).into()
}

fn item_ident(item: &Item) -> Option<&Ident> {
    match item {
        Item::Fn(item) => Some(&item.sig.ident),
        Item::Struct(item) => Some(&item.ident),
        Item::Enum(item) => Some(&item.ident),
        Item::Trait(item) => Some(&item.ident),
        Item::Union(item) => Some(&item.ident),
        Item::Const(item) => Some(&item.ident),
        Item::Static(item) => Some(&item.ident),
        Item::Mod(item) => Some(&item.ident),
        _ => None,
    }
}
