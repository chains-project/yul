package com.example.restapi.greeting;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(GreetingController.class)
class GreetingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createsAndListsGreetings() throws Exception {
        mockMvc.perform(post("/api/v1/greetings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"content":"Hello, World!"}
                                """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value(1))
                .andExpect(jsonPath("$.content").value("Hello, World!"));

        mockMvc.perform(get("/api/v1/greetings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].content").value("Hello, World!"));
    }

    @Test
    void rejectsBlankContent() throws Exception {
        mockMvc.perform(post("/api/v1/greetings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"content":""}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void returnsNotFoundForUnknownId() throws Exception {
        mockMvc.perform(get("/api/v1/greetings/{id}", 42))
                .andExpect(status().isNotFound());
    }
}
