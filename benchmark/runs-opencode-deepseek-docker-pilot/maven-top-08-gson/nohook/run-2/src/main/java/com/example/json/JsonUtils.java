package com.example.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.util.List;

/**
 * Thin wrapper around Jackson's {@link ObjectMapper} for reading and writing JSON.
 */
public final class JsonUtils {

    private static final ObjectMapper MAPPER = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

    private JsonUtils() {
    }

    public static ObjectMapper mapper() {
        return MAPPER;
    }

    /** Serialize any object to a pretty-printed JSON string. */
    public static String toJson(Object value) {
        try {
            return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Failed to serialize object to JSON", e);
        }
    }

    /** Parse a JSON string into the given type. */
    public static <T> T fromJson(String json, Class<T> type) {
        try {
            return MAPPER.readValue(json, type);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Failed to parse JSON into " + type.getName(), e);
        }
    }

    /** Parse a JSON array string into a list of the given element type. */
    public static <T> List<T> fromJsonList(String json, Class<T> elementType) {
        try {
            return MAPPER.readValue(json, MAPPER.getTypeFactory()
                    .constructCollectionType(List.class, elementType));
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Failed to parse JSON array into List<"
                    + elementType.getName() + ">", e);
        }
    }

    /** Parse a JSON string using a full generic type reference, e.g. {@code Map<String, User>}. */
    public static <T> T fromJson(String json, TypeReference<T> type) {
        try {
            return MAPPER.readValue(json, type);
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException("Failed to parse JSON", e);
        }
    }
}
