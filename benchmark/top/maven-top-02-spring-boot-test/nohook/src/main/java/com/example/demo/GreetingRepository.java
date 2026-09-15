package com.example.demo;

import org.springframework.stereotype.Repository;

@Repository
public class GreetingRepository {

    public String findGreeting() {
        return "Hello";
    }

}
