package org.genesis.pilot;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/** A deterministic, in-memory inventory for the single-threaded research pilot. */
public final class Inventory {
    private final Map<String, Integer> stock;

    public Inventory(Map<String, Integer> initialStock) {
        Objects.requireNonNull(initialStock, "initialStock");
        stock = new HashMap<>();
        initialStock.forEach((itemId, quantity) -> {
            requireItemId(itemId);
            if (quantity == null || quantity < 0) {
                throw new IllegalArgumentException("Stock must be a non-negative integer");
            }
            stock.put(itemId, quantity);
        });
    }

    public int availableStock(String itemId) {
        requireItemId(itemId);
        Integer available = stock.get(itemId);
        if (available == null) {
            throw new IllegalArgumentException("Unknown item: " + itemId);
        }
        return available;
    }

    public OrderReceipt placeOrder(String itemId, int quantity) {
        if (quantity <= 0) {
            throw new IllegalArgumentException("Order quantity must be positive");
        }
        int available = availableStock(itemId);
        if (quantity > available) {
            throw new IllegalStateException("Insufficient stock for: " + itemId);
        }
        int remaining = available - quantity;
        stock.put(itemId, remaining);
        return new OrderReceipt(itemId, quantity, remaining);
    }

    private static void requireItemId(String itemId) {
        if (itemId == null || itemId.isBlank()) {
            throw new IllegalArgumentException("Item ID must not be blank");
        }
    }

    public record OrderReceipt(String itemId, int quantity, int remainingStock) {}
}
