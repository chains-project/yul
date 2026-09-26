package com.example.demo;

import com.example.demo.model.Item;
import com.example.demo.repository.ItemRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class ItemRepositoryTest {

    @Autowired
    private ItemRepository itemRepository;

    @Test
    void savesAndFindsAnItem() {
        Item saved = itemRepository.save(new Item("widget"));

        assertThat(itemRepository.findById(saved.getId()))
                .isPresent()
                .get()
                .extracting(Item::getName)
                .isEqualTo("widget");
    }
}
