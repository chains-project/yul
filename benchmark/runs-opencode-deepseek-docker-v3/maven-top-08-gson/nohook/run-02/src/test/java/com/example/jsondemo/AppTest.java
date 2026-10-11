package com.example.jsondemo;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

class AppTest {

    private final ObjectMapper mapper = new ObjectMapper();

    @Test
    void serializesUserToJson() throws Exception {
        User user = new User(1L, "Ada Lovelace", "ada@example.com");

        String json = mapper.writeValueAsString(user);

        assertEquals("{\"id\":1,\"name\":\"Ada Lovelace\",\"email\":\"ada@example.com\"}", json);
    }

    @Test
    void deserializesUserFromJson() throws Exception {
        String json = "{\"id\":2,\"name\":\"Alan Turing\",\"email\":\"alan@example.com\"}";

        User user = mapper.readValue(json, User.class);

        assertEquals(2L, user.getId());
        assertEquals("Alan Turing", user.getName());
        assertEquals("alan@example.com", user.getEmail());
    }
}
