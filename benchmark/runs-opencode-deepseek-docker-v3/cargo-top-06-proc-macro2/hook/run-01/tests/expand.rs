use token_macro::make_answer;

#[test]
fn works_as_a_macro() {
    assert_eq!(make_answer!(42), 42);
}
