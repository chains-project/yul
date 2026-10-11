package com.example.jsonapp;

public final class App {

    public static void main(String[] args) throws Exception {
        JsonService json = new JsonService();

        User user = new User(1L, "Ada Lovelace", "ada@example.com");
        String encoded = json.toJson(user);
        System.out.println(encoded);

        User decoded = json.fromJson(encoded, User.class);
        System.out.println(decoded);
    }
}
