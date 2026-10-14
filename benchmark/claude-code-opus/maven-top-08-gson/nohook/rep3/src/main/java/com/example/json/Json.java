package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/**
 * Shared JSON entry point. {@link JsonMapper} is immutable and thread-safe,
 * so a single instance can be reused across the application.
 */
public final class Json {

    private static final JsonMapper MAPPER = JsonMapper.builder().build();

    private Json() {
    }

    public static JsonMapper mapper() {
        return MAPPER;
    }

    public static String toJson(Object value) {
        return MAPPER.writeValueAsString(value);
    }

    public static String toPrettyJson(Object value) {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }

    public static <T> T fromJson(String json, Class<T> type) {
        return MAPPER.readValue(json, type);
    }

    public static JsonNode parseTree(String json) {
        return MAPPER.readTree(json);
    }
}
