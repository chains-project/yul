package com.example.restapi.greeting;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class GreetingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createGreetingReturnsCreated() throws Exception {
        mockMvc.perform(post("/api/v1/greetings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"Ada\"}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.content").value("Hello, Ada!"));
    }

    @Test
    void createGreetingWithBlankNameReturnsBadRequest() throws Exception {
        mockMvc.perform(post("/api/v1/greetings")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\":\"\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void findUnknownGreetingReturnsNotFound() throws Exception {
        mockMvc.perform(get("/api/v1/greetings/{id}", 9999))
                .andExpect(status().isNotFound());
    }
}
