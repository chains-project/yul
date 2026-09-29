use proc_macro::TokenStream;
use quote::ToTokens;
use syn::parse::{Parse, ParseStream};
use syn::visit_mut::VisitMut;
use syn::{parse_macro_input, Ident, Item, Result, Token};

struct RenameInput {
    from: Ident,
    _arrow: Token![=>],
    to: Ident,
    _comma: Token![,],
    item: Item,
}

impl Parse for RenameInput {
    fn parse(input: ParseStream) -> Result<Self> {
        Ok(Self {
            from: input.parse()?,
            _arrow: input.parse()?,
            to: input.parse()?,
            _comma: input.parse()?,
            item: input.parse()?,
        })
    }
}

struct Renamer {
    from: String,
    to: Ident,
}

impl VisitMut for Renamer {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if *ident == self.from {
            let mut replacement = self.to.clone();
            replacement.set_span(ident.span());
            *ident = replacement;
        }
    }
}

#[proc_macro]
pub fn rename(input: TokenStream) -> TokenStream {
    let RenameInput { from, to, item, .. } = parse_macro_input!(input as RenameInput);
    let mut item = item;
    Renamer {
        from: from.to_string(),
        to,
    }
    .visit_item_mut(&mut item);
    item.into_token_stream().into()
}
