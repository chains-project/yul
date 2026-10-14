package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.SerializationFeature;
import tools.jackson.databind.json.JsonMapper;

/** Shared, thread-safe JSON helpers backed by a single Jackson mapper. */
public final class Json {

    private static final JsonMapper MAPPER = JsonMapper.builder().build();
    private static final JsonMapper PRETTY = MAPPER.rebuild()
            .enable(SerializationFeature.INDENT_OUTPUT)
            .build();

    private Json() {
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
        return PRETTY.writeValueAsString(value);
    }

    public static JsonMapper mapper() {
        return MAPPER;
    }
}
