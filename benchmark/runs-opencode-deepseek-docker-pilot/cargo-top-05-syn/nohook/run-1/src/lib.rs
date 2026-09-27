use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, parse_quote, Data, DeriveInput, Fields, ItemFn};

#[proc_macro_derive(TypeInfo)]
pub fn derive_type_info(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let ident = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let type_name = ident.to_string();
    let names: Vec<String> = match &input.data {
        Data::Struct(data) => field_names(&data.fields),
        Data::Enum(data) => data.variants.iter().map(|v| v.ident.to_string()).collect(),
        Data::Union(_) => {
            return syn::Error::new_spanned(ident, "TypeInfo cannot be derived for unions")
                .to_compile_error()
                .into()
        }
    };
    let names = names.iter().map(|name| quote!(#name));

    let expanded = quote! {
        impl #impl_generics #ident #ty_generics #where_clause {
            pub fn type_name() -> &'static str {
                #type_name
            }

            pub fn field_names() -> &'static [&'static str] {
                &[#(#names),*]
            }
        }
    };

    expanded.into()
}

fn field_names(fields: &Fields) -> Vec<String> {
    match fields {
        Fields::Named(named) => named
            .named
            .iter()
            .map(|field| field.ident.as_ref().expect("named field").to_string())
            .collect(),
        Fields::Unnamed(unnamed) => (0..unnamed.unnamed.len()).map(|i| i.to_string()).collect(),
        Fields::Unit => Vec::new(),
    }
}

#[proc_macro_attribute]
pub fn trace(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let mut function = parse_macro_input!(item as ItemFn);
    let name = function.sig.ident.clone();
    let body = function.block.clone();

    function.block = parse_quote!({
        eprintln!("[trace] entering {}", stringify!(#name));
        #body
    });

    quote!(#function).into()
}
