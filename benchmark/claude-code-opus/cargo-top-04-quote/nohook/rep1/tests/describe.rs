use codegen_macros::Describe;

#[derive(Describe)]
struct Wrapper<T: std::fmt::Debug> {
    value: T,
    label: &'static str,
}

#[test]
fn works_with_generics() {
    let w = Wrapper { value: vec![1, 2], label: "nums" };
    assert_eq!(Wrapper::<u8>::FIELD_NAMES, &["value", "label"]);
    assert_eq!(w.describe(), r#"Wrapper { value: [1, 2], label: "nums" }"#);
}
