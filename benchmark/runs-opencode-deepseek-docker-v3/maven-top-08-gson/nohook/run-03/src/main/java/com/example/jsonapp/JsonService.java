package com.example.jsonapp;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

public final class JsonService {

    private final ObjectMapper mapper;

    public JsonService() {
        this.mapper = new ObjectMapper()
                .enable(SerializationFeature.INDENT_OUTPUT);
    }

    public String toJson(Object value) throws JsonProcessingException {
        return mapper.writeValueAsString(value);
    }

    public <T> T fromJson(String json, Class<T> type) throws JsonProcessingException {
        return mapper.readValue(json, type);
    }
}
