package com.example.json;

import java.time.Instant;
import java.util.List;

public record User(
        long id,
        String name,
        String email,
        boolean active,
        Instant createdAt,
        List<String> roles) {
}
