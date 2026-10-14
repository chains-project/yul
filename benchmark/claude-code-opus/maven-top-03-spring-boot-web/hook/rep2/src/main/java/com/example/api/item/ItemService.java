package com.example.api.item;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Service;

/**
 * In-memory store used as a placeholder until a real persistence layer is added.
 */
@Service
public class ItemService {

    private final Map<Long, Item> items = new ConcurrentHashMap<>();
    private final AtomicLong nextId = new AtomicLong(1);

    public List<Item> findAll() {
        return items.values().stream()
                .sorted(Comparator.comparingLong(Item::id))
                .toList();
    }

    public Item findById(long id) {
        Item item = items.get(id);
        if (item == null) {
            throw new ItemNotFoundException(id);
        }
        return item;
    }

    public Item create(CreateItemRequest request) {
        Item item = new Item(nextId.getAndIncrement(), request.name(), request.description());
        items.put(item.id(), item);
        return item;
    }

    public void delete(long id) {
        if (items.remove(id) == null) {
            throw new ItemNotFoundException(id);
        }
    }
}
