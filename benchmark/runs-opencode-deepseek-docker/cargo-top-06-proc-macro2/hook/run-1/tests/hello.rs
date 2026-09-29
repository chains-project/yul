use my_proc_macro::Hello;

#[derive(Hello)]
struct Widget;

#[test]
fn derive_expands_and_is_usable() {
    assert_eq!(Widget::hello(), "Widget");
}
