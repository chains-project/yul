use stable_tokens_macros::count_tokens;

#[test]
fn expands_to_token_count() {
    assert_eq!(count_tokens!(a + b (c d)), 6);
}
