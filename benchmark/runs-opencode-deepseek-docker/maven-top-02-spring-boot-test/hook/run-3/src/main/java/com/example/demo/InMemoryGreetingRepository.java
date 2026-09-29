package com.example.demo;

import java.util.Map;
import org.springframework.stereotype.Repository;

@Repository
public class InMemoryGreetingRepository implements GreetingRepository {

    private static final Map<Long, String> NAMES = Map.of(
            1L, "World",
            2L, "Spring"
    );

    @Override
    public String findName(long id) {
        return NAMES.getOrDefault(id, "stranger");
    }
}
