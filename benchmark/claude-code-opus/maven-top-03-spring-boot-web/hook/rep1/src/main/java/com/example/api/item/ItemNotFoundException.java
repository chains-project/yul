package com.example.api.item;

public class ItemNotFoundException extends RuntimeException {

    public ItemNotFoundException(long id) {
        super("Item " + id + " not found");
    }
}
