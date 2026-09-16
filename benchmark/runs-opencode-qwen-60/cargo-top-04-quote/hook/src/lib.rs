use proc_macro::TokenStream;
use quote::quote;
use syn::parse_macro_input;

#[proc_macro]
pub fn my_macro(input: TokenStream) -> TokenStream {
    let parsed = parse_macro_input!(input as syn::ItemFn);
    let name = &parsed.sig.ident;
    let body = &parsed.block;

    quote! {
        fn #name() {
            println!("before");
            #body
            println!("after");
        }
    }
    .into()
}