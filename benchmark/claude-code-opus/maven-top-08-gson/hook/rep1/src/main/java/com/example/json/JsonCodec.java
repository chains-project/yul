package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.ObjectMapper;
import tools.jackson.databind.json.JsonMapper;

/** Thin wrapper around a shared, thread-safe Jackson mapper. */
public final class JsonCodec {

    private static final ObjectMapper MAPPER = JsonMapper.builder().build();

    private JsonCodec() {
    }

    public static <T> T parse(String json, Class<T> type) {
        return MAPPER.readValue(json, type);
    }

    public static JsonNode parseTree(String json) {
        return MAPPER.readTree(json);
    }

    public static String toJson(Object value) {
        return MAPPER.writeValueAsString(value);
    }

    public static String toPrettyJson(Object value) {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }
}
