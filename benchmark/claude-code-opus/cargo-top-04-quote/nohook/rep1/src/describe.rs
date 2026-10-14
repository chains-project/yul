use proc_macro2::TokenStream;
use quote::quote;
use syn::{Data, DeriveInput, Error, Fields, Result};

pub fn expand(input: &DeriveInput) -> Result<TokenStream> {
    let name = &input.ident;
    let (impl_generics, ty_generics, where_clause) = input.generics.split_for_impl();

    let Data::Struct(data) = &input.data else {
        return Err(Error::new_spanned(
            input,
            "`Describe` can only be derived for structs",
        ));
    };
    let Fields::Named(fields) = &data.fields else {
        return Err(Error::new_spanned(
            &data.fields,
            "`Describe` requires a struct with named fields",
        ));
    };

    let idents: Vec<_> = fields.named.iter().filter_map(|f| f.ident.as_ref()).collect();
    let names: Vec<String> = idents.iter().map(|i| i.to_string()).collect();
    let format = format!(
        "{} {{{{ {} }}}}",
        name,
        names.iter().map(|n| format!("{n}: {{:?}}")).collect::<Vec<_>>().join(", ")
    );

    Ok(quote! {
        impl #impl_generics #name #ty_generics #where_clause {
            pub const FIELD_NAMES: &'static [&'static str] = &[#(#names),*];

            pub fn describe(&self) -> ::std::string::String {
                ::std::format!(#format, #(self.#idents),*)
            }
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use syn::parse_quote;

    #[test]
    fn generates_impl_for_named_struct() {
        let input: DeriveInput = parse_quote! { struct Point { x: i32, y: i32 } };
        let out = expand(&input).unwrap().to_string();
        assert!(out.contains("impl Point"));
        assert!(out.contains("FIELD_NAMES"));
    }

    #[test]
    fn rejects_enums() {
        let input: DeriveInput = parse_quote! { enum E { A } };
        let err = expand(&input).unwrap_err();
        assert!(err.to_string().contains("only be derived for structs"));
    }
}
