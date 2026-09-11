package com.example;

import com.google.gson.Gson;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AppTest {

    record Point(int x, int y) {}

    @Test
    void roundTripsThroughJson() {
        Gson gson = new Gson();

        Point original = new Point(3, 4);
        String json = gson.toJson(original);
        Point parsed = gson.fromJson(json, Point.class);

        assertEquals(original, parsed);
    }
}
