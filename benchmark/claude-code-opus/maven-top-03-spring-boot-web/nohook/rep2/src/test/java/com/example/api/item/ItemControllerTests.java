package com.example.api.item;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.example.api.web.GlobalExceptionHandler;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

@WebMvcTest(ItemController.class)
@Import({ItemService.class, GlobalExceptionHandler.class})
class ItemControllerTests {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void createThenFetchItem() throws Exception {
        MvcResult result = mockMvc.perform(post("/api/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"name": "Widget", "description": "A useful widget"}
                                """))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.name").value("Widget"))
                .andReturn();
        long id = idOf(result);

        mockMvc.perform(get("/api/items/" + id))
                .andExpect(status().isOk())
                .andExpect(header().doesNotExist("Location"))
                .andExpect(jsonPath("$.description").value("A useful widget"));

        assertThat(result.getResponse().getHeader("Location"))
                .endsWith("/api/items/" + id);
    }

    @Test
    void updateAndDeleteItem() throws Exception {
        long id = createItem("Old");

        mockMvc.perform(put("/api/items/" + id)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"name": "New"}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("New"));

        mockMvc.perform(delete("/api/items/" + id))
                .andExpect(status().isNoContent());

        mockMvc.perform(get("/api/items/" + id))
                .andExpect(status().isNotFound());
    }

    @Test
    void missingItemReturnsProblemDetail() throws Exception {
        mockMvc.perform(get("/api/items/999999"))
                .andExpect(status().isNotFound())
                .andExpect(header().string("Content-Type", MediaType.APPLICATION_PROBLEM_JSON_VALUE))
                .andExpect(jsonPath("$.title").value("Resource not found"))
                .andExpect(jsonPath("$.detail").value("Item 999999 not found"));
    }

    @Test
    void invalidRequestReturnsBadRequest() throws Exception {
        mockMvc.perform(post("/api/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"name": ""}
                                """))
                .andExpect(status().isBadRequest());
    }

    private long createItem(String name) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/items")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"name\": \"" + name + "\"}"))
                .andExpect(status().isCreated())
                .andReturn();
        return idOf(result);
    }

    private static long idOf(MvcResult result) throws Exception {
        Number id = JsonPath.read(result.getResponse().getContentAsString(), "$.id");
        return id.longValue();
    }
}
