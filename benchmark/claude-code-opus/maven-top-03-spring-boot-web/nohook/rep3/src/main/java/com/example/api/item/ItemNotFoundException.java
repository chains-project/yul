package com.example.api.item;

public class ItemNotFoundException extends RuntimeException {

    public ItemNotFoundException(Long id) {
        super("Item " + id + " not found");
    }
}
