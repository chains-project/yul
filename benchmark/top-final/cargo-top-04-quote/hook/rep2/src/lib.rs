use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(HelloWorld)]
pub fn hello_world(input: TokenStream) -> TokenStream {
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;

    let expanded = quote! {
        impl #name {
            pub fn hello_world() {
                println!("Hello, World! My name is {}!", stringify!(#name));
            }
        }
    };

    expanded.into()
}
