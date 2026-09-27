package com.example.demo.greeting;

import java.util.Map;

import org.springframework.stereotype.Repository;

@Repository
public class InMemoryGreetingRepository implements GreetingRepository {

    private final Map<Long, String> names = Map.of(1L, "World", 2L, "Spring");

    @Override
    public String findName(long id) {
        return this.names.getOrDefault(id, "there");
    }

}
