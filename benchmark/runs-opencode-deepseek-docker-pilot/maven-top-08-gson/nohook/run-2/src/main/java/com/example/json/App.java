package com.example.json;

import java.time.Instant;
import java.util.List;

public final class App {

    private App() {
    }

    public static void main(String[] args) {
        User user = new User(
                42L,
                "Ada Lovelace",
                "ada@example.com",
                List.of("admin", "developer"),
                Instant.parse("2026-01-15T09:30:00Z"));

        String json = JsonUtils.toJson(user);
        System.out.println("Generated JSON:");
        System.out.println(json);

        User parsed = JsonUtils.fromJson(json, User.class);
        System.out.println("Parsed back: " + parsed);
        System.out.println("Round-trip equal: " + user.equals(parsed));
    }
}
