use rust_transform::{
    collect_fn_names, collect_int_literals, double_int_literals_file, parse_file, to_token_stream,
};
use rust_transform_example::{answer, computed};
use rust_transform_macro::inspect_fn_names;

#[test]
fn attribute_macro_doubles_literals() {
    assert_eq!(answer(), 42);
}

#[test]
fn function_like_macro_doubles_items() {
    assert_eq!(computed(), 22);
}

const NAMES: [&str; 2] = inspect_fn_names! {
    fn alpha() {}
    fn beta() {}
};

#[test]
fn inspection_macro_reports_names() {
    assert_eq!(NAMES, ["alpha", "beta"]);
}

#[test]
fn core_library_parses_inspects_and_transforms() {
    let source = "fn one() -> i32 { 1 }\nfn two() -> i32 { 2 }";
    let mut file = parse_file(source).expect("valid source");

    assert_eq!(collect_fn_names(&file), ["one", "two"]);

    double_int_literals_file(&mut file);
    assert_eq!(collect_int_literals(&file), [2, 4]);

    let rendered = to_token_stream(&file).to_string();
    assert!(rendered.contains("42") || rendered.contains("4"));
}
