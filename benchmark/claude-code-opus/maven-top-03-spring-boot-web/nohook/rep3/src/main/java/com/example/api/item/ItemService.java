package com.example.api.item;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Service;

/**
 * In-memory store. Replace with a Spring Data repository when adding persistence.
 */
@Service
public class ItemService {

    private final Map<Long, Item> items = new ConcurrentHashMap<>();
    private final AtomicLong nextId = new AtomicLong(1);

    public List<Item> findAll() {
        return items.values().stream()
                .sorted((a, b) -> Long.compare(a.id(), b.id()))
                .toList();
    }

    public Item findById(Long id) {
        Item item = items.get(id);
        if (item == null) {
            throw new ItemNotFoundException(id);
        }
        return item;
    }

    public Item create(ItemRequest request) {
        long id = nextId.getAndIncrement();
        Item item = new Item(id, request.name(), request.description());
        items.put(id, item);
        return item;
    }

    public Item update(Long id, ItemRequest request) {
        findById(id);
        Item item = new Item(id, request.name(), request.description());
        items.put(id, item);
        return item;
    }

    public void delete(Long id) {
        if (items.remove(id) == null) {
            throw new ItemNotFoundException(id);
        }
    }
}
