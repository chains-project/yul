use my_macro::make_answer;

make_answer!(
    pub fn answer() -> u32 {
        0
    }
);

#[test]
fn macro_expands_in_a_real_crate() {
    assert_eq!(answer(), 42);
}
