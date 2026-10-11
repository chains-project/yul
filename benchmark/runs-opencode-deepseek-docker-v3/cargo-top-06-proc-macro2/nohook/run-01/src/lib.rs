use proc_macro::TokenStream;

mod expand;

#[proc_macro_derive(Greet)]
pub fn derive_greet(input: TokenStream) -> TokenStream {
    expand::greet(input.into()).into()
}
