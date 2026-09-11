package com.example.springdatajpa;

import com.example.springdatajpa.entity.Product;
import com.example.springdatajpa.repository.ProductRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class ProductRepositoryTests {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void savesAndReadsBackAProduct() {
        Product saved = productRepository.save(new Product("Keyboard", 49.99));

        assertThat(saved.getId()).isNotNull();
        assertThat(productRepository.findById(saved.getId()))
                .get()
                .extracting(Product::getName)
                .isEqualTo("Keyboard");
    }
}
