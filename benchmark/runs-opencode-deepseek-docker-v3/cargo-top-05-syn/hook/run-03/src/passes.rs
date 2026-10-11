//! Syntax-tree inspection and transformation passes.
//!
//! A pass is any type implementing [`syn::visit_mut::VisitMut`]. Add new passes
//! to [`transform_file`] and they will run in order over the whole tree.

use syn::{
    visit_mut::{self, VisitMut},
    File, Ident, ItemFn,
};

/// Run every transformation pass over `file` and return the rewritten tree.
pub fn transform_file(mut file: File) -> File {
    RenameFunctions.visit_file_mut(&mut file);
    file
}

/// Inspect the tree and append `_transformed` to every free function's name.
///
/// `visit_mut` recurses into nested modules, so functions in inline `mod`
/// blocks are rewritten too.
struct RenameFunctions;

impl VisitMut for RenameFunctions {
    fn visit_item_fn_mut(&mut self, node: &mut ItemFn) {
        let renamed = format!("{}_transformed", node.sig.ident);
        node.sig.ident = Ident::new(&renamed, node.sig.ident.span());
        visit_mut::visit_item_fn_mut(self, node);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use quote::ToTokens;

    fn parse(src: &str) -> File {
        syn::parse_str(src).expect("test input is valid Rust")
    }

    #[test]
    fn renames_free_functions() {
        let rendered = transform_file(parse("fn foo() {}"))
            .into_token_stream()
            .to_string();
        assert!(rendered.contains("fn foo_transformed"), "got: {rendered}");
    }

    #[test]
    fn leaves_other_items_untouched() {
        let rendered = transform_file(parse("struct Foo;"))
            .into_token_stream()
            .to_string();
        assert!(rendered.contains("struct Foo"), "got: {rendered}");
    }

    #[test]
    fn recurses_into_inline_modules() {
        let rendered = transform_file(parse("mod inner { fn bar() {} }"))
            .into_token_stream()
            .to_string();
        assert!(rendered.contains("fn bar_transformed"), "got: {rendered}");
    }
}
