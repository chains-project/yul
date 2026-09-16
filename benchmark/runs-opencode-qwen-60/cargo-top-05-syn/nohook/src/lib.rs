use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, ItemMod};

/// A simple example procedural macro that demonstrates parsing and transforming
/// Rust source code into a syntax tree that can be inspected and transformed.
#[proc_macro]
pub fn example_macro(input: TokenStream) -> TokenStream {
    // Parse the input TokenStream into a syntax tree (syn::ItemMod)
    let input_module = parse_macro_input!(input as ItemMod);

    // Inspect the parsed syntax tree
    let module_name = &input_module.ident;
    let items: &[syn::Item] = input_module
        .content
        .as_ref()
        .map(|(_, items)| items.as_slice())
        .unwrap_or(&[]);

    // Transform the syntax tree and generate new code
    let expanded = quote! {
        mod #module_name {
            #(
                #items
            )*

            // Your transformations go here
        }
    };

    // Return the transformed code as a TokenStream
    expanded.into()
}