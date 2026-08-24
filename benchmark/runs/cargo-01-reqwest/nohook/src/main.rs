use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct Post {
    id: u32,
    title: String,
}

#[tokio::main]
async fn main() -> Result<(), reqwest::Error> {
    let client = reqwest::Client::new();

    let post: Post = client
        .get("https://jsonplaceholder.typicode.com/posts/1")
        .send()
        .await?
        .json()
        .await?;

    println!("{:#?}", post);

    Ok(())
}
