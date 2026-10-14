package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/** Shared, thread-safe JSON helpers backed by Jackson. */
public final class Json {

    private static final JsonMapper MAPPER = JsonMapper.builder().build();

    private Json() {
    }

    public static JsonMapper mapper() {
        return MAPPER;
    }

    public static <T> T parse(String json, Class<T> type) {
        return MAPPER.readValue(json, type);
    }

    public static JsonNode parseTree(String json) {
        return MAPPER.readTree(json);
    }

    public static String write(Object value) {
        return MAPPER.writeValueAsString(value);
    }

    public static String writePretty(Object value) {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }
}
