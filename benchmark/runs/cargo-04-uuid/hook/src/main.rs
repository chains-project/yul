use uuid::Uuid;

fn generate_request_id() -> String {
    Uuid::new_v4().to_string()
}

fn main() {
    let request_id = generate_request_id();
    println!("request_id={request_id}");
}
