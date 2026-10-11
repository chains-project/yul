package com.example.demo;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(GreetingController.class)
class GreetingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private GreetingService greetingService;

    @Test
    void greetReturnsServiceResponse() throws Exception {
        given(greetingService.greet("Ada")).willReturn("Hi, Ada!");

        mockMvc.perform(get("/greet").param("name", "Ada"))
                .andExpect(status().isOk())
                .andExpect(content().string("Hi, Ada!"));

        verify(greetingService).greet("Ada");
    }

    @Test
    void mockDefaultsToStubbedValue() {
        GreetingService plainMock = org.mockito.Mockito.mock(GreetingService.class);
        given(plainMock.greet("Bob")).willReturn("Hey Bob");

        assertThat(plainMock.greet("Bob")).isEqualTo("Hey Bob");
        assertThat(plainMock.greet("Someone else")).isNull();
    }
}
