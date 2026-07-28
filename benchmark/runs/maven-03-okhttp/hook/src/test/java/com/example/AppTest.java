package com.example;

import mockwebserver3.MockResponse;
import mockwebserver3.MockWebServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

import java.io.IOException;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AppTest {

    private MockWebServer server;
    private OkHttpClient client;

    @BeforeEach
    void setUp() throws IOException {
        server = new MockWebServer();
        server.start();
        client = new OkHttpClient();
    }

    @AfterEach
    void tearDown() throws IOException {
        server.close();
    }

    @Test
    void getRequestReturnsExpectedBody() throws IOException {
        server.enqueue(new MockResponse.Builder().body("{\"userId\":1,\"id\":1,\"completed\":false}").build());

        Request request = new Request.Builder()
                .url(server.url("/todos/1"))
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            assertEquals(200, response.code());
            assertEquals("{\"userId\":1,\"id\":1,\"completed\":false}", response.body().string());
        }
    }
}
