use proc_macro::TokenStream;
use proc_macro2::TokenStream as TokenStream2;
use quote::quote;
use syn::{parse_macro_input, Field, Ident, ItemFn};

fn getter_impl(field: &Field) -> TokenStream2 {
    let name = field.ident.as_ref().expect("only named fields supported");
    let ty = &field.ty;
    let getter = Ident::new(&format!("get_{}", name), name.span());
    quote! {
        pub fn #getter(&self) -> &#ty {
            &self.#name
        }
    }
}

#[proc_macro]
pub fn make_fn(input: TokenStream) -> TokenStream {
    let name = parse_macro_input!(input as Ident);
    quote! {
        pub fn #name() -> &'static str {
            stringify!(#name)
        }
    }
    .into()
}

#[proc_macro_attribute]
pub fn with_name(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as ItemFn);
    let name = &input.sig.ident;
    let const_name = Ident::new(&name.to_string().to_uppercase(), name.span());
    quote! {
        #input
        pub const #const_name: &str = stringify!(#name);
    }
    .into()
}

#[proc_macro_derive(Getters)]
pub fn derive_getters(item: TokenStream) -> TokenStream {
    let input = parse_macro_input!(item as syn::DeriveInput);
    let name = &input.ident;
    let getters = match &input.data {
        syn::Data::Struct(data) => data.fields.iter().map(getter_impl).collect::<Vec<_>>(),
        _ => panic!("Getters can only be derived for structs"),
    };
    quote! {
        impl #name {
            #(#getters)*
        }
    }
    .into()
}
