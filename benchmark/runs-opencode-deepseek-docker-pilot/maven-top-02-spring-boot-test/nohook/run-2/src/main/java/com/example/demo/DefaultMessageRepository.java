package com.example.demo;

import org.springframework.stereotype.Repository;

@Repository
public class DefaultMessageRepository implements MessageRepository {

    @Override
    public String findTemplate() {
        return "Hello";
    }
}
