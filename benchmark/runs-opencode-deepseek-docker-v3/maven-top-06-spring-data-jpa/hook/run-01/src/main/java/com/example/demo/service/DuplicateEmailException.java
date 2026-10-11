package com.example.demo.service;

public class DuplicateEmailException extends RuntimeException {

    public DuplicateEmailException(String email) {
        super("Customer already exists with email: " + email);
    }
}
