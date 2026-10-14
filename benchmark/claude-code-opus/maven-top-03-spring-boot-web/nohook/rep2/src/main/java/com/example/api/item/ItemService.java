package com.example.api.item;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

import org.springframework.stereotype.Service;

/**
 * In-memory item store. Replace with a Spring Data repository when adding persistence.
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

    public Item create(ItemRequest request) {
        long id = nextId.getAndIncrement();
        Item item = new Item(id, request.name(), request.description());
        items.put(id, item);
        return item;
    }

    public Item update(long id, ItemRequest request) {
        Item updated = items.computeIfPresent(id, (key, existing) ->
                new Item(id, request.name(), request.description()));
        if (updated == null) {
            throw new ItemNotFoundException(id);
        }
        return updated;
    }

    public void delete(long id) {
        if (items.remove(id) == null) {
            throw new ItemNotFoundException(id);
        }
    }
}
