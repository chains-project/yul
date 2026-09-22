package com.example.demo.book;

public class DuplicateIsbnException extends RuntimeException {

    public DuplicateIsbnException(String isbn) {
        super("A book with isbn already exists: " + isbn);
    }
}
