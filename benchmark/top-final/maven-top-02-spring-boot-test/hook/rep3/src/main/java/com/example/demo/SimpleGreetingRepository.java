package com.example.demo;

import org.springframework.stereotype.Repository;

@Repository
public class SimpleGreetingRepository implements GreetingRepository {

    @Override
    public String findGreetingFor(String name) {
        return "Hello, " + name + "!";
    }

}
