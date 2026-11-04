package org.genesis.pilot;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class InventoryTest {
    @Test
    void initialStockIsCopiedAndCallerMapIsNotChangedByOrders() {
        Map<String, Integer> initial = new HashMap<>(Map.of("BOOK", 8));
        Inventory inventory = new Inventory(initial);
        initial.put("BOOK", 99);
        assertEquals(8, inventory.availableStock("BOOK"));
        inventory.placeOrder("BOOK", 2);
        assertEquals(99, initial.get("BOOK"));
        assertEquals(6, inventory.availableStock("BOOK"));
    }

    @Test
    void successfulOrderReturnsReceiptAndChangesOnlySelectedItem() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8, "PEN", 3));
        assertEquals(new Inventory.OrderReceipt("BOOK", 2, 6),
                inventory.placeOrder("BOOK", 2));
        assertEquals(6, inventory.availableStock("BOOK"));
        assertEquals(3, inventory.availableStock("PEN"));
    }

    @Test
    void nonPositiveOrdersAreRejectedWithoutChangingStock() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8));
        for (int quantity : new int[] {0, -1, Integer.MIN_VALUE}) {
            assertThrows(IllegalArgumentException.class,
                    () -> inventory.placeOrder("BOOK", quantity));
            assertEquals(8, inventory.availableStock("BOOK"));
        }
    }

    @Test
    void unknownItemCannotBeReadOrOrderedAndExistingStockIsPreserved() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8));
        assertThrows(IllegalArgumentException.class,
                () -> inventory.availableStock("MISSING"));
        assertThrows(IllegalArgumentException.class,
                () -> inventory.placeOrder("MISSING", 1));
        assertEquals(8, inventory.availableStock("BOOK"));
    }

    @Test
    void insufficientStockRejectsOrderWithoutChangingAnyItem() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8, "PEN", 3));
        assertThrows(IllegalStateException.class, () -> inventory.placeOrder("BOOK", 9));
        assertEquals(8, inventory.availableStock("BOOK"));
        assertEquals(3, inventory.availableStock("PEN"));
    }

    @Test
    void exactStockOrderSucceedsAndFurtherOrderIsRejected() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8));
        assertEquals(new Inventory.OrderReceipt("BOOK", 8, 0),
                inventory.placeOrder("BOOK", 8));
        assertEquals(0, inventory.availableStock("BOOK"));
        assertThrows(IllegalStateException.class, () -> inventory.placeOrder("BOOK", 1));
        assertEquals(0, inventory.availableStock("BOOK"));
    }

    @Test
    void invalidItemIdsAreRejectedWithoutChangingStock() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8));
        for (String itemId : new String[] {null, "", "  "}) {
            assertThrows(IllegalArgumentException.class, () -> inventory.availableStock(itemId));
            assertThrows(IllegalArgumentException.class, () -> inventory.placeOrder(itemId, 1));
            assertEquals(8, inventory.availableStock("BOOK"));
        }
    }

    @Test
    void invalidInitialStockCannotConstructAnInventory() {
        assertThrows(NullPointerException.class, () -> new Inventory(null));
        assertThrows(IllegalArgumentException.class, () -> new Inventory(Map.of("BOOK", -1)));
        assertThrows(IllegalArgumentException.class, () -> new Inventory(Map.of(" ", 1)));
        Map<String, Integer> nullQuantity = new HashMap<>();
        nullQuantity.put("BOOK", null);
        assertThrows(IllegalArgumentException.class, () -> new Inventory(nullQuantity));
        Map<String, Integer> nullId = new HashMap<>();
        nullId.put(null, 1);
        assertThrows(IllegalArgumentException.class, () -> new Inventory(nullId));
    }

    @Test
    void sequentialOrdersConsumeStockAndRejectedOrderDoesNotUndoSuccess() {
        Inventory inventory = new Inventory(Map.of("BOOK", 8));
        inventory.placeOrder("BOOK", 3);
        inventory.placeOrder("BOOK", 4);
        assertThrows(IllegalStateException.class, () -> inventory.placeOrder("BOOK", 2));
        assertEquals(1, inventory.availableStock("BOOK"));
        assertEquals(new Inventory.OrderReceipt("BOOK", 1, 0), inventory.placeOrder("BOOK", 1));
    }

    @Test
    void maximumIntegerAndInitiallyEmptyStockHaveDefinedBehavior() {
        Inventory inventory = new Inventory(Map.of("MAX", Integer.MAX_VALUE, "EMPTY", 0));
        assertEquals(new Inventory.OrderReceipt("MAX", Integer.MAX_VALUE, 0),
                inventory.placeOrder("MAX", Integer.MAX_VALUE));
        assertThrows(IllegalStateException.class, () -> inventory.placeOrder("EMPTY", 1));
        assertEquals(0, inventory.availableStock("MAX"));
        assertEquals(0, inventory.availableStock("EMPTY"));
    }
}
