package com.example.jpademo.repository;

import com.example.jpademo.model.Product;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
class ProductRepositoryTests {

    @Autowired
    private ProductRepository productRepository;

    @Test
    void savesAndFindsProductsByName() {
        productRepository.save(new Product("Mechanical Keyboard", 129.99));
        productRepository.save(new Product("Wireless Mouse", 39.99));

        List<Product> matches = productRepository.findByNameContainingIgnoreCase("keyboard");

        assertThat(matches).hasSize(1);
        assertThat(matches.get(0).getName()).isEqualTo("Mechanical Keyboard");
    }

}
