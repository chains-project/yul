package com.example.demo;

import org.springframework.stereotype.Repository;

@Repository
public class InMemoryGreetingRepository implements GreetingRepository {

    @Override
    public String findNameById(long id) {
        return "World";
    }

}
