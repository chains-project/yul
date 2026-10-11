package com.example.json;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.time.Instant;
import java.util.List;
import java.util.Map;

public final class JsonDemo {

    private static final ObjectMapper MAPPER = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
            .disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES);

    public static String toJson(Object value) {
        try {
            return MAPPER.writeValueAsString(value);
        } catch (Exception e) {
            throw new JsonException("Failed to serialize to JSON", e);
        }
    }

    public static String toPrettyJson(Object value) {
        try {
            return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
        } catch (Exception e) {
            throw new JsonException("Failed to serialize to JSON", e);
        }
    }

    public static <T> T fromJson(String json, Class<T> type) {
        try {
            return MAPPER.readValue(json, type);
        } catch (Exception e) {
            throw new JsonException("Failed to deserialize JSON", e);
        }
    }

    public static <T> T fromJson(String json, TypeReference<T> type) {
        try {
            return MAPPER.readValue(json, type);
        } catch (Exception e) {
            throw new JsonException("Failed to deserialize JSON", e);
        }
    }

    public static void main(String[] args) {
        User user = new User(
                42L,
                "Ada Lovelace",
                "ada@example.com",
                true,
                Instant.parse("2026-01-15T10:30:00Z"),
                List.of("admin", "developer"));

        String json = toPrettyJson(user);
        System.out.println("Generated JSON:");
        System.out.println(json);

        User parsed = fromJson(json, User.class);
        System.out.println("Parsed back: " + parsed);

        String raw = "{\"name\":\"Grace Hopper\",\"languages\":[\"COBOL\",\"FLOW-MATIC\"]}";
        Map<String, Object> tree = fromJson(raw, new TypeReference<>() {
        });
        System.out.println("Parsed generic JSON: " + tree);
    }

    private JsonDemo() {
    }
}
