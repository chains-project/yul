package com.example.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

public final class JsonDemo {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private JsonDemo() {
    }

    public static void main(String[] args) throws Exception {
        Person person = new Person("Ada Lovelace", 36, "ada@example.com");

        String json = toJson(person);
        System.out.println("Generated JSON: " + json);
        System.out.println("Pretty JSON:\n" + toPrettyJson(person));

        Person parsed = fromJson(json, Person.class);
        System.out.println("Parsed object:  " + parsed);

        JsonNode tree = parseTree(json);
        System.out.println("Tree name:      " + tree.get("name").asText());
    }

    public static String toJson(Object value) throws Exception {
        return MAPPER.writeValueAsString(value);
    }

    public static String toPrettyJson(Object value) throws Exception {
        return MAPPER.writerWithDefaultPrettyPrinter().writeValueAsString(value);
    }

    public static <T> T fromJson(String json, Class<T> type) throws Exception {
        return MAPPER.readValue(json, type);
    }

    public static JsonNode parseTree(String json) throws Exception {
        return MAPPER.readTree(json);
    }

    public static String toJsonWithExtraField(Person person, String key, String value) throws Exception {
        ObjectNode node = MAPPER.valueToTree(person);
        node.put(key, value);
        return toJson(node);
    }
}
