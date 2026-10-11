package com.example.jsonapp.model;

import java.time.Instant;
import java.util.List;

public record Person(
        long id,
        String name,
        String email,
        Instant createdAt,
        List<String> roles) {
}
