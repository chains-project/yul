use token_macros::Describe;

#[derive(Describe)]
struct Widget;

#[test]
fn derives_describe() {
    assert_eq!(Widget::describe(), "Widget");
}
