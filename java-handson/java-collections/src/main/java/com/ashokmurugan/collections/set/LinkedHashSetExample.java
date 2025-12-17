package com.ashokmurugan.collections.set;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.Arrays;

/**
 * LinkedHashSet Example - Hash Table + Linked List Based Set Implementation
 * 
 * EXPLANATION:
 * LinkedHashSet is a hash table and linked list implementation of Set
 * interface.
 * It maintains a doubly-linked list running through all entries to preserve
 * insertion order.
 * Combines the best of HashSet (fast operations) and ordered iteration.
 * 
 * KEY CHARACTERISTICS:
 * - Implements Set, Cloneable, Serializable
 * - No duplicate elements allowed
 * - Maintains insertion order (predictable iteration order)
 * - Allows one null element
 * - Not synchronized (not thread-safe)
 * - Slightly slower than HashSet due to linked list maintenance
 * 
 * INTERNAL STRUCTURE:
 * - Uses LinkedHashMap internally
 * - Each entry has: hash, key, value, next (hash chain), before, after
 * (insertion order)
 * - Doubly-linked list connects all entries in insertion order
 * - Default initial capacity: 16
 * - Default load factor: 0.75
 * 
 * TIME COMPLEXITY:
 * - add(E e) : O(1) average, O(n) worst case
 * - remove(Object o) : O(1) average, O(n) worst case
 * - contains(Object o) : O(1) average, O(n) worst case
 * - size() : O(1)
 * - iteration : O(n) - faster than HashSet (only visits entries, not empty
 * buckets)
 * 
 * SPACE COMPLEXITY: O(n) - slightly more than HashSet due to linked list
 * pointers
 * 
 * WHEN TO USE:
 * ✓ Need unique elements with predictable iteration order
 * ✓ Need to maintain insertion order
 * ✓ Fast operations like HashSet but with order
 * ✓ Implementing LRU cache
 * ✗ Don't care about order (use HashSet - slightly faster)
 * ✗ Need sorted order (use TreeSet)
 * 
 * HASHSET vs LINKEDHASHSET vs TREESET:
 * - HashSet: Fastest, no order
 * - LinkedHashSet: Fast, maintains insertion order
 * - TreeSet: Slower, maintains sorted order
 */
public class LinkedHashSetExample {

    public static void main(String[] args) {
        System.out.println("=== LinkedHashSet Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Insertion Order Preservation
        demonstrateInsertionOrder();

        // 3. Basic Operations
        demonstrateBasicOperations();

        // 4. Comparison with HashSet
        demonstrateHashSetComparison();

        // 5. Iteration Performance
        demonstrateIterationPerformance();

        // 6. Practical Use Cases
        demonstratePracticalUseCases();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor
        LinkedHashSet<String> set1 = new LinkedHashSet<>();
        System.out.println("Empty LinkedHashSet: " + set1);

        // Constructor with initial capacity
        LinkedHashSet<Integer> set2 = new LinkedHashSet<>(32);
        System.out.println("LinkedHashSet with capacity 32: " + set2);

        // Constructor with capacity and load factor
        LinkedHashSet<String> set3 = new LinkedHashSet<>(32, 0.8f);
        System.out.println("LinkedHashSet with capacity 32, load factor 0.8: " + set3);

        // Constructor with collection
        LinkedHashSet<String> set4 = new LinkedHashSet<>(Arrays.asList("C", "A", "B"));
        System.out.println("LinkedHashSet from collection: " + set4 + " (maintains order)");

        System.out.println();
    }

    private static void demonstrateInsertionOrder() {
        System.out.println("2. INSERTION ORDER PRESERVATION");
        System.out.println("--------------------------------");

        LinkedHashSet<Integer> linkedSet = new LinkedHashSet<>();
        java.util.HashSet<Integer> hashSet = new java.util.HashSet<>();

        // Add elements in specific order
        int[] numbers = { 5, 2, 8, 1, 9, 3, 7, 4, 6 };

        for (int num : numbers) {
            linkedSet.add(num);
            hashSet.add(num);
        }

        System.out.println("Insertion order: " + Arrays.toString(numbers));
        System.out.println("LinkedHashSet:   " + linkedSet + " (maintains order)");
        System.out.println("HashSet:         " + hashSet + " (no order guarantee)");

        // Verify iteration order
        System.out.print("\nLinkedHashSet iteration: ");
        for (int num : linkedSet) {
            System.out.print(num + " ");
        }
        System.out.println("(same as insertion order)");

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("3. BASIC OPERATIONS");
        System.out.println("-------------------");

        LinkedHashSet<String> fruits = new LinkedHashSet<>();

        // Adding elements - maintains insertion order
        fruits.add("Apple");
        fruits.add("Banana");
        fruits.add("Cherry");
        fruits.add("Date");
        System.out.println("After adding: " + fruits);

        // Adding duplicate - no effect, order unchanged
        boolean added = fruits.add("Banana");
        System.out.println("Added duplicate Banana: " + added);
        System.out.println("Set: " + fruits + " (order unchanged)");

        // Contains - O(1)
        boolean hasApple = fruits.contains("Apple");
        System.out.println("Contains Apple: " + hasApple);

        // Remove - O(1), order of remaining elements preserved
        boolean removed = fruits.remove("Banana");
        System.out.println("Removed Banana: " + removed);
        System.out.println("After removal: " + fruits + " (order preserved)");

        // Re-adding removed element - goes to end
        fruits.add("Banana");
        System.out.println("Re-added Banana: " + fruits + " (added at end)");

        // Size
        System.out.println("Size: " + fruits.size());

        // Clear
        LinkedHashSet<String> temp = new LinkedHashSet<>(fruits);
        temp.clear();
        System.out.println("After clear: " + temp);

        System.out.println();
    }

    private static void demonstrateHashSetComparison() {
        System.out.println("4. COMPARISON WITH HASHSET");
        System.out.println("---------------------------");

        String[] words = { "zebra", "apple", "mango", "banana", "kiwi" };

        LinkedHashSet<String> linkedSet = new LinkedHashSet<>();
        java.util.HashSet<String> hashSet = new java.util.HashSet<>();

        for (String word : words) {
            linkedSet.add(word);
            hashSet.add(word);
        }

        System.out.println("Input order: " + Arrays.toString(words));
        System.out.println();

        System.out.print("LinkedHashSet: ");
        for (String word : linkedSet) {
            System.out.print(word + " ");
        }
        System.out.println("(insertion order)");

        System.out.print("HashSet:       ");
        for (String word : hashSet) {
            System.out.print(word + " ");
        }
        System.out.println("(random order)");

        // Both have same performance for basic operations
        System.out.println("\nPerformance:");
        System.out.println("- add/remove/contains: Both O(1)");
        System.out.println("- LinkedHashSet: Slightly slower due to linked list maintenance");
        System.out.println("- LinkedHashSet: Faster iteration (only visits entries)");

        System.out.println();
    }

    private static void demonstrateIterationPerformance() {
        System.out.println("5. ITERATION PERFORMANCE");
        System.out.println("------------------------");

        // Create sets with sparse data
        LinkedHashSet<Integer> linkedSet = new LinkedHashSet<>();
        java.util.HashSet<Integer> hashSet = new java.util.HashSet<>();

        // Add only 1000 elements (but HashSet has capacity for many more)
        for (int i = 0; i < 1000; i++) {
            linkedSet.add(i);
            hashSet.add(i);
        }

        // LinkedHashSet iteration - only visits actual entries
        long start = System.nanoTime();
        int sum1 = 0;
        for (int num : linkedSet) {
            sum1 += num;
        }
        long end = System.nanoTime();
        long linkedTime = (end - start) / 1000;
        System.out.println("LinkedHashSet iteration: " + linkedTime + " μs");

        // HashSet iteration - may visit empty buckets
        start = System.nanoTime();
        int sum2 = 0;
        for (int num : hashSet) {
            sum2 += num;
        }
        end = System.nanoTime();
        long hashTime = (end - start) / 1000;
        System.out.println("HashSet iteration:       " + hashTime + " μs");

        System.out.println("\nLinkedHashSet is often faster for iteration");
        System.out.println("because it only visits actual entries, not empty buckets");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("6. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Remove duplicates while preserving order
        String[] array = { "apple", "banana", "apple", "cherry", "banana", "date" };
        LinkedHashSet<String> uniqueOrdered = new LinkedHashSet<>(Arrays.asList(array));

        System.out.println("Original array: " + Arrays.toString(array));
        System.out.println("Unique (ordered): " + uniqueOrdered);

        // Use Case 2: Track visited items in order
        LinkedHashSet<String> visitHistory = new LinkedHashSet<>();
        visitHistory.add("Home");
        visitHistory.add("Products");
        visitHistory.add("About");
        visitHistory.add("Products"); // Duplicate, won't be added
        visitHistory.add("Contact");

        System.out.println("\nBrowser history (unique pages in order):");
        int i = 1;
        for (String page : visitHistory) {
            System.out.println("  " + i++ + ". " + page);
        }

        // Use Case 3: Maintaining unique tags in order
        LinkedHashSet<String> tags = new LinkedHashSet<>();
        tags.add("java");
        tags.add("collections");
        tags.add("tutorial");
        tags.add("java"); // Duplicate
        tags.add("examples");

        System.out.println("\nArticle tags: " + String.join(", ", tags));

        // Use Case 4: Processing stream of events (unique, in order)
        String[] events = { "login", "view_page", "click", "view_page", "logout" };
        LinkedHashSet<String> uniqueEvents = new LinkedHashSet<>();

        System.out.println("\nEvent stream: " + Arrays.toString(events));
        for (String event : events) {
            if (uniqueEvents.add(event)) {
                System.out.println("  First occurrence: " + event);
            }
        }
        System.out.println("Unique events in order: " + uniqueEvents);

        // Use Case 5: LRU-like behavior (simple version)
        class RecentItems<T> {
            private final LinkedHashSet<T> items;
            private final int maxSize;

            RecentItems(int maxSize) {
                this.items = new LinkedHashSet<>();
                this.maxSize = maxSize;
            }

            void add(T item) {
                // Remove if exists (to re-add at end)
                items.remove(item);
                items.add(item);

                // Remove oldest if exceeds max size
                if (items.size() > maxSize) {
                    T oldest = items.iterator().next();
                    items.remove(oldest);
                }
            }

            @Override
            public String toString() {
                return items.toString();
            }
        }

        RecentItems<String> recentFiles = new RecentItems<>(3);
        recentFiles.add("file1.txt");
        recentFiles.add("file2.txt");
        recentFiles.add("file3.txt");
        System.out.println("\nRecent files: " + recentFiles);

        recentFiles.add("file4.txt"); // file1.txt removed
        System.out.println("After adding file4: " + recentFiles);

        recentFiles.add("file2.txt"); // file2.txt moved to end
        System.out.println("After re-opening file2: " + recentFiles);

        System.out.println("\n=== End of LinkedHashSet Example ===");
    }
}
