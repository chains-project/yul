package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Thin wrapper around a shared, thread-safe Jackson mapper. */
public final class Json {

    private static final JsonMapper MAPPER = JsonMapper.builder().build();

    private Json() {
    }

    /** Parses JSON into the given type. */
    public static <T> T parse(String json, Class<T> type) {
        return MAPPER.readValue(json, type);
    }

    /** Parses JSON into a tree when no fixed type exists. */
    public static JsonNode parseTree(String json) {
        return MAPPER.readTree(json);
    }

    /** Serializes a value to compact JSON. */
    public static String write(Object value) {
        return MAPPER.writeValueAsString(value);
    }

    /** Serializes a value to indented JSON. */
    public static String writePretty(Object value) {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }
}
