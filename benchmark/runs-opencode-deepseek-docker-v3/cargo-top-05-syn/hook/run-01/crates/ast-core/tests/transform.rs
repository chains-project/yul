use ast_core::{inspect, parse_item, parse_source, transform};

#[test]
fn parses_and_inspects_a_file() {
    let file = parse_source("fn add(a: i32, b: i32) -> i32 { a + b }").unwrap();

    assert_eq!(inspect::item_count(&file), 1);

    let idents = inspect::collect_identifiers(&file);
    for expected in ["add", "a", "b", "i32"] {
        assert!(
            idents.contains(&expected.to_owned()),
            "missing `{expected}` in {idents:?}",
        );
    }
}

#[test]
fn parses_a_single_item() {
    let item = parse_item("struct Point { x: i32, y: i32 }").unwrap();
    assert!(matches!(item, syn::Item::Struct(_)));
}

#[test]
fn rename_replaces_every_occurrence() {
    let mut file = parse_source("fn add(a: i32, b: i32) -> i32 { a + b }").unwrap();

    transform::rename_in_file(&mut file, "a", "x");

    let idents = inspect::collect_identifiers(&file);
    assert!(idents.contains(&"x".to_owned()));
    assert!(!idents.contains(&"a".to_owned()));
    assert!(idents.contains(&"b".to_owned()));
}

#[test]
fn rename_preserves_unrelated_syntax() {
    let mut file = parse_source("fn f() -> i32 { let value = 1; value }").unwrap();

    transform::rename_in_file(&mut file, "value", "renamed");

    let idents = inspect::collect_identifiers(&file);
    assert!(idents.contains(&"renamed".to_owned()));
    assert!(!idents.contains(&"value".to_owned()));
}

#[test]
fn invalid_source_is_an_error() {
    assert!(parse_source("fn broken( {").is_err());
}
