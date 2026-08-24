use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct Post {
    id: u32,
    title: String,
}

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    let url = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "https://jsonplaceholder.typicode.com/posts/1".to_string());

    let post = reqwest::get(&url).await?.json::<Post>().await?;

    println!("[{}] {}", post.id, post.title);

    Ok(())
}
