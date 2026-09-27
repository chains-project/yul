package com.example.inventory.web;

import com.example.inventory.domain.Product;
import com.example.inventory.service.ProductService;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping
    public List<ProductResponse> list(@RequestParam(required = false) String name) {
        return service.searchByName(name).stream().map(ProductResponse::from).toList();
    }

    @GetMapping("/{id}")
    public ProductResponse get(@PathVariable Long id) {
        return ProductResponse.from(service.findById(id));
    }

    @GetMapping("/by-sku/{sku}")
    public ProductResponse getBySku(@PathVariable String sku) {
        return ProductResponse.from(service.findBySku(sku));
    }

    @PostMapping
    public ResponseEntity<ProductResponse> create(@Valid @RequestBody ProductRequest request) {
        Product created = service.create(toEntity(request));
        return ResponseEntity.created(URI.create("/api/products/" + created.getId()))
                .body(ProductResponse.from(created));
    }

    @PutMapping("/{id}")
    public ProductResponse update(@PathVariable Long id, @Valid @RequestBody ProductRequest request) {
        return ProductResponse.from(service.update(id, toEntity(request)));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }

    private Product toEntity(ProductRequest request) {
        return new Product(request.sku(), request.name(), request.price(), request.quantity());
    }
}
