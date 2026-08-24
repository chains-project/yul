use uuid::Uuid;

/// Generates a new request ID, to be attached to each incoming request
/// (e.g. as an `X-Request-Id` header) for tracing/logging purposes.
fn generate_request_id() -> String {
    Uuid::new_v4().to_string()
}

fn main() {
    let request_id = generate_request_id();
    println!("request_id={request_id}");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn generates_unique_ids() {
        let a = generate_request_id();
        let b = generate_request_id();
        assert_ne!(a, b);
        assert!(Uuid::parse_str(&a).is_ok());
    }
}
