//! In-place transformations of a syntax tree, built on
//! [`syn::visit_mut::VisitMut`].

use syn::visit_mut::{self, VisitMut};
use syn::{File, Ident, Item};

/// Renames every occurrence of one identifier to another.
///
/// Spans are preserved, so compiler diagnostics produced after the
/// transformation still point at the original source location.
#[derive(Debug, Clone)]
pub struct RenameIdent {
    from: String,
    to: String,
}

impl RenameIdent {
    /// Create a renamer mapping `from` to `to`.
    pub fn new(from: impl Into<String>, to: impl Into<String>) -> Self {
        Self {
            from: from.into(),
            to: to.into(),
        }
    }
}

impl VisitMut for RenameIdent {
    fn visit_ident_mut(&mut self, ident: &mut Ident) {
        if ident == self.from.as_str() {
            let span = ident.span();
            *ident = Ident::new(&self.to, span);
        }
        visit_mut::visit_ident_mut(self, ident);
    }
}

/// Rename `from` to `to` throughout a parsed file.
pub fn rename_in_file(file: &mut File, from: &str, to: &str) {
    RenameIdent::new(from, to).visit_file_mut(file);
}

/// Rename `from` to `to` throughout a single parsed item.
pub fn rename_in_item(item: &mut Item, from: &str, to: &str) {
    RenameIdent::new(from, to).visit_item_mut(item);
}
