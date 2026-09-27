use proc_macro::TokenStream;
use syn::{parse_macro_input, DeriveInput};

mod expand;

#[proc_macro_derive(Describe)]
pub fn describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    expand::describe(&input).into()
}
