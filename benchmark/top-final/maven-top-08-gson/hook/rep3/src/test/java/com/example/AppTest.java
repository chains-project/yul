package com.example;

import com.google.gson.Gson;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AppTest {

    @Test
    void roundTripsThroughJson() {
        Gson gson = new Gson();
        App.Person original = new App.Person("Grace Hopper", 85);

        String json = gson.toJson(original);
        App.Person parsed = gson.fromJson(json, App.Person.class);

        assertEquals(original, parsed);
    }
}
