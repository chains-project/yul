extern crate proc_macro;

use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, ItemFn};

#[proc_macro_attribute]
pub fn hook(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let name = &input.sig.ident;
    let inputs = &input.sig.inputs;
    let output = &input.sig.output;
    let body = &input.block;
    let attrs = &input.attrs;

    let expanded = quote! {
        #(#attrs)*
        fn #name ( #inputs ) #output {
            // hook: pre-execution instrumentation
            eprintln!("entering {}", #name);

            #body

            // hook: post-execution instrumentation
            eprintln!("exiting {}", #name);
        }
    };

    expanded.into()
}