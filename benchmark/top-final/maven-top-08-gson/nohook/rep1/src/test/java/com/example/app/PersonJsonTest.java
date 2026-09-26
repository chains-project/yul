package com.example.app;

import com.google.gson.Gson;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;

class PersonJsonTest {

    @Test
    void roundTripsThroughJson() {
        Gson gson = new Gson();
        Person original = new Person("Grace Hopper", 85, List.of("grace@example.com"));

        String json = gson.toJson(original);
        Person parsed = gson.fromJson(json, Person.class);

        assertEquals(original.getName(), parsed.getName());
        assertEquals(original.getAge(), parsed.getAge());
        assertEquals(original.getEmails(), parsed.getEmails());
    }
}
