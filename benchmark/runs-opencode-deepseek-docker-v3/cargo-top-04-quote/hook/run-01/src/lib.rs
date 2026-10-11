use proc_macro::TokenStream;
use quote::quote;
use syn::parse::{Parse, ParseStream};
use syn::{Data, DeriveInput, Fields, Ident, Token, Type, parse_macro_input};

#[proc_macro_derive(CodeGen)]
pub fn derive_codegen(input: TokenStream) -> TokenStream {
    let input = parse_macro_input!(input as DeriveInput);
    match expand_codegen(&input) {
        Ok(tokens) => tokens.into(),
        Err(err) => err.to_compile_error().into(),
    }
}

fn expand_codegen(input: &DeriveInput) -> syn::Result<proc_macro2::TokenStream> {
    let name = &input.ident;
    let names = generated_names(&input.data);
    let count = names.len();

    Ok(quote! {
        impl #name {
            pub const FIELD_COUNT: usize = #count;

            pub fn field_names() -> &'static [&'static str] {
                &[#(#names),*]
            }
        }
    })
}

fn generated_names(data: &Data) -> Vec<String> {
    match data {
        Data::Struct(data) => match &data.fields {
            Fields::Named(fields) => fields
                .named
                .iter()
                .filter_map(|field| field.ident.as_ref())
                .map(ToString::to_string)
                .collect(),
            Fields::Unnamed(_) | Fields::Unit => Vec::new(),
        },
        Data::Enum(data) => data
            .variants
            .iter()
            .map(|variant| variant.ident.to_string())
            .collect(),
        Data::Union(_) => Vec::new(),
    }
}

struct StructSpec {
    name: Ident,
    fields: Vec<(Ident, Type)>,
}

impl Parse for StructSpec {
    fn parse(input: ParseStream) -> syn::Result<Self> {
        let name: Ident = input.parse()?;
        let content;
        syn::braced!(content in input);

        let mut fields = Vec::new();
        while !content.is_empty() {
            let field: Ident = content.parse()?;
            content.parse::<Token![:]>()?;
            let ty: Type = content.parse()?;
            fields.push((field, ty));

            if content.peek(Token![,]) {
                content.parse::<Token![,]>()?;
            } else {
                break;
            }
        }

        Ok(StructSpec { name, fields })
    }
}

#[proc_macro]
pub fn make_struct(input: TokenStream) -> TokenStream {
    let spec = parse_macro_input!(input as StructSpec);
    let name = &spec.name;
    let field_names: Vec<&Ident> = spec.fields.iter().map(|(ident, _)| ident).collect();
    let field_types: Vec<&Type> = spec.fields.iter().map(|(_, ty)| ty).collect();

    quote! {
        #[derive(Debug, Clone, PartialEq, Eq)]
        pub struct #name {
            #(pub #field_names: #field_types),*
        }

        impl #name {
            pub fn new(#(#field_names: #field_types),*) -> Self {
                Self { #(#field_names),* }
            }
        }
    }
    .into()
}
