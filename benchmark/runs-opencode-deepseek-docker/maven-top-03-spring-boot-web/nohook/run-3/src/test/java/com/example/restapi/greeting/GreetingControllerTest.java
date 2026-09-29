package com.example.restapi.greeting;

import static org.hamcrest.Matchers.is;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(GreetingController.class)
class GreetingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void greetReturnsDefaultGreeting() throws Exception {
        mockMvc.perform(get("/api/greetings"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", is("Hello, World!")));
    }

    @Test
    void greetUsesProvidedName() throws Exception {
        mockMvc.perform(get("/api/greetings").param("name", "Alice"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", is("Hello, Alice!")));
    }
}
