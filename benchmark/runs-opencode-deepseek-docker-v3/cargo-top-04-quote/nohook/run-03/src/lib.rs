use proc_macro::TokenStream;
use quote::quote;
use syn::{
    parse::{Parse, ParseStream},
    parse_macro_input,
    punctuated::Punctuated,
    DeriveInput, Ident, Token,
};

#[proc_macro_derive(Describe)]
pub fn derive_describe(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let field_names: Vec<String> = match &input.data {
        syn::Data::Struct(data) => data
            .fields
            .iter()
            .filter_map(|field| field.ident.as_ref().map(|ident| ident.to_string()))
            .collect(),
        _ => Vec::new(),
    };

    let expanded = quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub fn describe(&self) -> ::std::vec::Vec<&'static str> {
                ::std::vec![#(#field_names),*]
            }
        }
    };

    expanded.into()
}

struct EnumDef {
    name: Ident,
    variants: Punctuated<Ident, Token![,]>,
}

impl Parse for EnumDef {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let name = input.parse()?;
        input.parse::<Token![:]>()?;
        let variants = Punctuated::parse_terminated(input)?;
        Ok(EnumDef { name, variants })
    }
}

#[proc_macro]
pub fn define_enum(input: TokenStream) -> TokenStream {
    let EnumDef { name, variants } = parse_macro_input!(input as EnumDef);
    let variant_idents: Vec<&Ident> = variants.iter().collect();

    let expanded = quote! {
        #[derive(Debug, Clone, Copy, PartialEq, Eq)]
        pub enum #name {
            #(#variant_idents),*
        }

        impl #name {
            pub fn from_name(name: &str) -> ::std::option::Option<Self> {
                match name {
                    #(::std::stringify!(#variant_idents) => ::std::option::Option::Some(Self::#variant_idents),)*
                    _ => ::std::option::Option::None,
                }
            }

            pub fn name(&self) -> &'static str {
                match self {
                    #(Self::#variant_idents => ::std::stringify!(#variant_idents),)*
                }
            }
        }
    };

    expanded.into()
}
