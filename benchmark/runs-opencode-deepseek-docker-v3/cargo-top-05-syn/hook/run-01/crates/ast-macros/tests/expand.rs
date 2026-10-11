use ast_macros::{ast_info, rename};

#[rename(a, x)]
fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[test]
fn rename_macro_rewrites_items() {
    assert_eq!(add(1, 2), 3);
}

const INFO: &str = ast_info!(
    fn add(a: i32, b: i32) -> i32 {
        a + b
    }
);

#[test]
fn ast_info_macro_reports_identifiers() {
    assert!(INFO.starts_with("items=1"), "{INFO}");
    assert!(INFO.contains("add"), "{INFO}");
    assert!(INFO.contains("i32"), "{INFO}");
}
