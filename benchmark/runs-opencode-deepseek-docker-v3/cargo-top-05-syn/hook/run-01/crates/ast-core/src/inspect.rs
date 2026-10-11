//! Read-only inspection of a syntax tree, built on [`syn::visit::Visit`].

use std::collections::BTreeSet;

use syn::visit::{self, Visit};
use syn::{File, Ident};

/// Collects every identifier that appears in a syntax tree.
///
/// Names are de-duplicated and sorted, which makes the result suitable for
/// snapshot testing and for driving later transformations.
#[derive(Debug, Default, Clone)]
pub struct IdentCollector {
    names: BTreeSet<String>,
}

impl IdentCollector {
    /// Create an empty collector.
    pub fn new() -> Self {
        Self::default()
    }

    /// Iterate over the collected names in sorted order.
    pub fn names(&self) -> impl Iterator<Item = &str> {
        self.names.iter().map(String::as_str)
    }

    /// Consume the collector, returning the names in sorted order.
    pub fn into_names(self) -> Vec<String> {
        self.names.into_iter().collect()
    }

    /// Number of distinct identifiers seen so far.
    pub fn len(&self) -> usize {
        self.names.len()
    }

    /// Whether no identifiers have been seen.
    pub fn is_empty(&self) -> bool {
        self.names.is_empty()
    }
}

impl<'ast> Visit<'ast> for IdentCollector {
    fn visit_ident(&mut self, ident: &'ast Ident) {
        self.names.insert(ident.to_string());
        visit::visit_ident(self, ident);
    }
}

/// Collect every distinct identifier in `file`, sorted.
pub fn collect_identifiers(file: &File) -> Vec<String> {
    let mut collector = IdentCollector::new();
    collector.visit_file(file);
    collector.into_names()
}

/// Count the top-level items in `file`.
pub fn item_count(file: &File) -> usize {
    file.items.len()
}
