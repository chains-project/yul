use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::{format_ident, quote};
use syn::parse::{Parse, ParseStream};
use syn::{parse_macro_input, Ident, LitInt, Result, Token};

/// Builds a function that adds `amount` to its argument.
///
/// This is the reusable code-generation routine. It is kept separate from the
/// macro entry point so the same token stream can be produced from other
/// macros or callers (for example, from another proc macro or a build script).
fn generate_adder(name: &Ident, amount: i64) -> TokenStream2 {
    quote! {
        pub fn #name(x: i64) -> i64 {
            x + #amount
        }
    }
}

struct AdderInput {
    name: Ident,
    _comma: Token![,],
    amount: LitInt,
}

impl Parse for AdderInput {
    fn parse(input: ParseStream) -> Result<Self> {
        Ok(AdderInput {
            name: input.parse()?,
            _comma: input.parse()?,
            amount: input.parse()?,
        })
    }
}

/// Generates a function from a name and an integer literal.
///
/// ```ignore
/// make_adder!(add_three, 3);
/// // expands to:
/// // pub fn add_three(x: i64) -> i64 { x + 3 }
/// ```
#[proc_macro]
pub fn make_adder(input: TokenStream) -> TokenStream {
    let AdderInput { name, amount, .. } = parse_macro_input!(input as AdderInput);
    let amount = amount.base10_parse::<i64>().unwrap();
    generate_adder(&name, amount).into()
}

/// Derive macro that adds a `describe` inherent method returning the type name.
#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let item = parse_macro_input!(input as syn::DeriveInput);
    let name = &item.ident;
    let type_name = format_ident!("{}", name);

    quote! {
        impl #name {
            pub fn describe() -> &'static str {
                stringify!(#type_name)
            }
        }
    }
    .into()
}
