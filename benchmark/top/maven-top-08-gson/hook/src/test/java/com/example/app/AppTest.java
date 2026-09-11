package com.example.app;

import com.google.gson.Gson;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class AppTest {

    @Test
    void roundTripsJson() {
        Gson gson = new Gson();
        App.Person person = new App.Person("Grace Hopper", 85);

        String json = gson.toJson(person);
        App.Person parsed = gson.fromJson(json, App.Person.class);

        assertEquals(person.name, parsed.name);
        assertEquals(person.age, parsed.age);
    }
}
