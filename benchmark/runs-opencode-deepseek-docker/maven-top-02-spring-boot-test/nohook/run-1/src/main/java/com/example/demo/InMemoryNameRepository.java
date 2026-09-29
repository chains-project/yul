package com.example.demo;

import java.util.Map;
import org.springframework.stereotype.Repository;

@Repository
public class InMemoryNameRepository implements NameRepository {

    private static final Map<Long, String> NAMES = Map.of(
            1L, "Alice",
            2L, "Bob");

    @Override
    public String findName(long id) {
        return NAMES.getOrDefault(id, "World");
    }

}
