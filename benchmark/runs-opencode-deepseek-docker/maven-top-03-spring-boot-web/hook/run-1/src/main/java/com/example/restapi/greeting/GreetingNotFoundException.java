package com.example.restapi.greeting;

public class GreetingNotFoundException extends RuntimeException {

    public GreetingNotFoundException(long id) {
        super("Greeting %d not found".formatted(id));
    }
}
