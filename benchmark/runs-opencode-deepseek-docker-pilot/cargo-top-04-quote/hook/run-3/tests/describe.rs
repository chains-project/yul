use codegen_macros::{declare_fields, Describe};

declare_fields!("Widget");

#[derive(Describe)]
struct Point {
    x: i32,
    y: i32,
    label: String,
}

#[test]
fn generated_struct_compiles() {
    let w = Widget::new(42);
    assert_eq!(w.value, 42);
}

#[test]
fn derive_reports_fields() {
    let p = Point {
        x: 1,
        y: 2,
        label: String::from("origin"),
    };
    assert_eq!(p.x, 1);
    assert_eq!(p.y, 2);
    assert_eq!(p.label, "origin");
    assert_eq!(Point::describe_fields(), vec!["x", "y", "label"]);
}
