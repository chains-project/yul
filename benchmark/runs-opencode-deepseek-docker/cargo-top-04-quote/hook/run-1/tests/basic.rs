use codegen_macro::{define_struct, Describe};

#[allow(dead_code)]
#[derive(Describe)]
struct Named {
    a: u8,
    b: String,
}

#[allow(dead_code)]
#[derive(Describe)]
struct Tuple(u8, u16);

#[allow(dead_code)]
#[derive(Describe)]
struct Unit;

define_struct! {
    pub struct Generated {
        pub x: i32,
        pub y: i32,
    }
}

#[test]
fn derive_reports_named_fields() {
    assert_eq!(Named::field_names(), &["a", "b"]);
}

#[test]
fn derive_reports_tuple_fields() {
    assert_eq!(Tuple::field_names(), &["0", "1"]);
}

#[test]
fn derive_reports_unit_fields() {
    let empty: &[&str] = &[];
    assert_eq!(Unit::field_names(), empty);
}

#[test]
fn function_like_macro_emits_struct() {
    assert_eq!(Generated::field_names(), &["x", "y"]);
}
