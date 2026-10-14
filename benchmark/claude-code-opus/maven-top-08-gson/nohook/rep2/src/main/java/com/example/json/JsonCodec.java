package com.example.json;

import tools.jackson.databind.JsonNode;
import tools.jackson.databind.SerializationFeature;
import tools.jackson.databind.json.JsonMapper;

/**
 * Thin wrapper around a shared, thread-safe Jackson {@link JsonMapper}.
 */
public final class JsonCodec {

    private static final JsonMapper MAPPER = JsonMapper.builder().build();
    private static final JsonMapper PRETTY = MAPPER.rebuild()
            .enable(SerializationFeature.INDENT_OUTPUT)
            .build();

    private JsonCodec() {
    }

    public static String toJson(Object value) {
        return MAPPER.writeValueAsString(value);
    }

    public static String toPrettyJson(Object value) {
        return PRETTY.writeValueAsString(value);
    }

    public static <T> T fromJson(String json, Class<T> type) {
        return MAPPER.readValue(json, type);
    }

    public static JsonNode parseTree(String json) {
        return MAPPER.readTree(json);
    }
}
