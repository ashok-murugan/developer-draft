package com.ashokmurugan.collections.concurrent;

import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.IntStream;

/**
 * ConcurrentHashMap Example - Thread-Safe Hash Table Implementation
 * 
 * EXPLANATION:
 * ConcurrentHashMap is a thread-safe variant of HashMap that allows concurrent
 * access
 * without locking the entire map. It uses lock striping (segment-based locking
 * in Java 7,
 * CAS operations and synchronized blocks in Java 8+).
 * 
 * KEY CHARACTERISTICS:
 * - Implements ConcurrentMap, Map interfaces
 * - Thread-safe without synchronizing entire map
 * - Better concurrency than Hashtable or Collections.synchronizedMap
 * - Does NOT allow null keys or values
 * - Weakly consistent iterators (don't throw ConcurrentModificationException)
 * - Atomic operations: putIfAbsent, remove, replace
 * 
 * INTERNAL STRUCTURE (Java 8+):
 * - Array of Node<K,V>[] (similar to HashMap)
 * - Uses CAS (Compare-And-Swap) operations for lock-free updates
 * - Synchronized blocks only when necessary (e.g., during resize)
 * - Each bin can be a linked list or TreeNode (red-black tree)
 * - Default initial capacity: 16
 * - Default concurrency level: 16 (deprecated in Java 8)
 * 
 * CONCURRENCY MECHANISM:
 * - Read operations: Lock-free (volatile reads)
 * - Write operations: Fine-grained locking per bin
 * - CAS for simple updates
 * - Synchronized for complex operations (tree conversion, resize)
 * 
 * TIME COMPLEXITY:
 * - get(key) : O(1) average - lock-free
 * - put(key, value) : O(1) average - may use CAS or lock
 * - remove(key) : O(1) average - may use CAS or lock
 * - putIfAbsent() : O(1) average - atomic operation
 * - compute() : O(1) average - atomic operation
 * - size() : O(1) - approximate count
 * - containsKey() : O(1) average - lock-free
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of entries
 * 
 * WHEN TO USE:
 * ✓ High concurrency scenarios
 * ✓ More reads than writes
 * ✓ Need thread-safe map without full synchronization
 * ✓ Atomic compound operations needed
 * ✗ Need null keys or values (use ConcurrentSkipListMap with wrapper)
 * ✗ Need strong consistency guarantees
 * 
 * CONCURRENTHASHMAP vs HASHTABLE vs SYNCHRONIZEDMAP:
 * - ConcurrentHashMap: Best performance, fine-grained locking, weakly
 * consistent
 * - Hashtable: Legacy, full synchronization, slow
 * - SynchronizedMap: Full synchronization, wrapper around HashMap
 */
public class ConcurrentHashMapExample {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== ConcurrentHashMap Comprehensive Example ===\n");

        // 1. Creation and Basic Operations
        demonstrateCreation();

        // 2. Thread-Safe Operations
        demonstrateThreadSafety();

        // 3. Atomic Operations
        demonstrateAtomicOperations();

        // 4. Concurrent Modifications
        demonstrateConcurrentModifications();

        // 5. Bulk Operations
        demonstrateBulkOperations();

        // 6. Performance Comparison
        demonstratePerformanceComparison();

        // 7. Practical Use Cases
        demonstratePracticalUseCases();

        // 8. Best Practices
        demonstrateBestPractices();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND BASIC OPERATIONS");
        System.out.println("---------------------------------");

        // Default constructor
        ConcurrentHashMap<String, Integer> map1 = new ConcurrentHashMap<>();
        System.out.println("Empty ConcurrentHashMap: " + map1);

        // Constructor with initial capacity
        ConcurrentHashMap<String, String> map2 = new ConcurrentHashMap<>(32);
        System.out.println("With capacity 32: " + map2);

        // Constructor with initial capacity and load factor
        ConcurrentHashMap<Integer, String> map3 = new ConcurrentHashMap<>(32, 0.75f);
        System.out.println("With capacity 32, load factor 0.75: " + map3);

        // Constructor with initial capacity, load factor, and concurrency level
        ConcurrentHashMap<String, Integer> map4 = new ConcurrentHashMap<>(32, 0.75f, 16);
        System.out.println("With capacity 32, load factor 0.75, concurrency 16: " + map4);

        // Basic operations
        map1.put("Alice", 30);
        map1.put("Bob", 25);
        map1.put("Charlie", 35);
        System.out.println("\nAfter adding: " + map1);

        // Get operation - thread-safe, lock-free
        Integer age = map1.get("Alice");
        System.out.println("Alice's age: " + age);

        // Remove operation
        Integer removed = map1.remove("Bob");
        System.out.println("Removed Bob: " + removed);
        System.out.println("After removal: " + map1);

        System.out.println();
    }

    private static void demonstrateThreadSafety() throws InterruptedException {
        System.out.println("2. THREAD-SAFE OPERATIONS");
        System.out.println("--------------------------");

        ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();
        java.util.HashMap<String, Integer> regularMap = new java.util.HashMap<>();

        // Test with ConcurrentHashMap
        System.out.println("Testing ConcurrentHashMap with 10 threads...");
        Thread[] threads1 = new Thread[10];
        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            threads1[i] = new Thread(() -> {
                for (int j = 0; j < 100; j++) {
                    concurrentMap.put("Key" + (threadId * 100 + j), j);
                }
            });
            threads1[i].start();
        }

        for (Thread t : threads1) {
            t.join();
        }

        System.out.println("ConcurrentHashMap size: " + concurrentMap.size());
        System.out.println("Expected: 1000, Actual: " + concurrentMap.size());
        System.out.println("Thread-safe: " + (concurrentMap.size() == 1000));

        // Test with regular HashMap (will likely fail or throw exception)
        System.out.println("\nTesting regular HashMap with 10 threads...");
        Thread[] threads2 = new Thread[10];
        AtomicInteger exceptionCount = new AtomicInteger(0);

        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            threads2[i] = new Thread(() -> {
                try {
                    for (int j = 0; j < 100; j++) {
                        regularMap.put("Key" + (threadId * 100 + j), j);
                    }
                } catch (Exception e) {
                    exceptionCount.incrementAndGet();
                }
            });
            threads2[i].start();
        }

        for (Thread t : threads2) {
            t.join();
        }

        System.out.println("Regular HashMap size: " + regularMap.size());
        System.out.println("Expected: 1000, Actual: " + regularMap.size());
        System.out.println("Exceptions occurred: " + exceptionCount.get());
        System.out.println("Thread-safe: " + (regularMap.size() == 1000 && exceptionCount.get() == 0));

        System.out.println();
    }

    private static void demonstrateAtomicOperations() {
        System.out.println("3. ATOMIC OPERATIONS");
        System.out.println("--------------------");

        ConcurrentHashMap<String, Integer> scores = new ConcurrentHashMap<>();
        scores.put("Alice", 100);
        scores.put("Bob", 90);

        System.out.println("Initial scores: " + scores);

        // putIfAbsent - atomic operation
        Integer oldValue = scores.putIfAbsent("Alice", 150);
        System.out.println("\nputIfAbsent('Alice', 150): " + oldValue + " (not updated)");

        Integer newValue = scores.putIfAbsent("Charlie", 85);
        System.out.println("putIfAbsent('Charlie', 85): " + newValue + " (added)");
        System.out.println("After putIfAbsent: " + scores);

        // replace - atomic operation
        boolean replaced = scores.replace("Alice", 100, 105);
        System.out.println("\nreplace('Alice', 100, 105): " + replaced);
        System.out.println("After replace: " + scores);

        // compute - atomic operation
        scores.compute("Alice", (key, value) -> value == null ? 0 : value + 10);
        System.out.println("\ncompute('Alice', v -> v + 10): " + scores.get("Alice"));

        // computeIfPresent - atomic operation
        scores.computeIfPresent("Bob", (key, value) -> value + 5);
        System.out.println("computeIfPresent('Bob', v -> v + 5): " + scores.get("Bob"));

        // computeIfAbsent - atomic operation
        scores.computeIfAbsent("David", key -> 80);
        System.out.println("computeIfAbsent('David', k -> 80): " + scores.get("David"));

        // merge - atomic operation
        scores.merge("Alice", 20, (oldVal, newVal) -> oldVal + newVal);
        System.out.println("\nmerge('Alice', 20, sum): " + scores.get("Alice"));

        System.out.println("\nFinal scores: " + scores);

        System.out.println();
    }

    private static void demonstrateConcurrentModifications() throws InterruptedException {
        System.out.println("4. CONCURRENT MODIFICATIONS");
        System.out.println("----------------------------");

        ConcurrentHashMap<Integer, String> map = new ConcurrentHashMap<>();

        // Populate map
        for (int i = 0; i < 100; i++) {
            map.put(i, "Value" + i);
        }

        System.out.println("Initial size: " + map.size());

        // Concurrent iteration and modification (safe with ConcurrentHashMap)
        Thread reader = new Thread(() -> {
            System.out.println("Reader thread: Iterating...");
            int count = 0;
            for (Map.Entry<Integer, String> entry : map.entrySet()) {
                count++;
                try {
                    Thread.sleep(1); // Simulate work
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            System.out.println("Reader thread: Iterated " + count + " entries (no exception)");
        });

        Thread writer = new Thread(() -> {
            System.out.println("Writer thread: Modifying...");
            for (int i = 100; i < 150; i++) {
                map.put(i, "Value" + i);
                try {
                    Thread.sleep(1); // Simulate work
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            System.out.println("Writer thread: Added 50 entries");
        });

        reader.start();
        writer.start();

        reader.join();
        writer.join();

        System.out.println("Final size: " + map.size());
        System.out.println("No ConcurrentModificationException thrown!");

        System.out.println();
    }

    private static void demonstrateBulkOperations() {
        System.out.println("5. BULK OPERATIONS (Java 8+)");
        System.out.println("-----------------------------");

        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();
        map.put("A", 1);
        map.put("B", 2);
        map.put("C", 3);
        map.put("D", 4);
        map.put("E", 5);

        System.out.println("Original map: " + map);

        // forEach - parallel iteration
        System.out.print("\nforEach: ");
        map.forEach((key, value) -> System.out.print(key + "=" + value + " "));
        System.out.println();

        // search - parallel search
        String result = map.search(1, (key, value) -> value > 3 ? key : null);
        System.out.println("search (value > 3): " + result);

        // reduce - parallel reduction
        Integer sum = map.reduce(1,
                (key, value) -> value,
                (v1, v2) -> v1 + v2);
        System.out.println("reduce (sum of values): " + sum);

        // forEachKey - parallel key iteration
        System.out.print("forEachKey: ");
        map.forEachKey(1, key -> System.out.print(key + " "));
        System.out.println();

        // forEachValue - parallel value iteration
        System.out.print("forEachValue: ");
        map.forEachValue(1, value -> System.out.print(value + " "));
        System.out.println();

        // mappingCount - approximate size
        long count = map.mappingCount();
        System.out.println("\nmappingCount: " + count);

        System.out.println();
    }

    private static void demonstratePerformanceComparison() throws InterruptedException {
        System.out.println("6. PERFORMANCE COMPARISON");
        System.out.println("-------------------------");

        int iterations = 100000;
        int threads = 10;

        // ConcurrentHashMap
        ConcurrentHashMap<Integer, Integer> concurrentMap = new ConcurrentHashMap<>();
        long start = System.nanoTime();

        Thread[] cThreads = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            final int threadId = i;
            cThreads[i] = new Thread(() -> {
                for (int j = 0; j < iterations / threads; j++) {
                    concurrentMap.put(threadId * (iterations / threads) + j, j);
                }
            });
            cThreads[i].start();
        }

        for (Thread t : cThreads) {
            t.join();
        }

        long concurrentTime = (System.nanoTime() - start) / 1000000;
        System.out.println(
                "ConcurrentHashMap (" + threads + " threads, " + iterations + " ops): " + concurrentTime + " ms");

        // Synchronized HashMap
        Map<Integer, Integer> syncMap = java.util.Collections.synchronizedMap(new java.util.HashMap<>());
        start = System.nanoTime();

        Thread[] sThreads = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            final int threadId = i;
            sThreads[i] = new Thread(() -> {
                for (int j = 0; j < iterations / threads; j++) {
                    syncMap.put(threadId * (iterations / threads) + j, j);
                }
            });
            sThreads[i].start();
        }

        for (Thread t : sThreads) {
            t.join();
        }

        long syncTime = (System.nanoTime() - start) / 1000000;
        System.out.println("SynchronizedMap (" + threads + " threads, " + iterations + " ops): " + syncTime + " ms");

        System.out.println(
                "\nConcurrentHashMap is " + String.format("%.2fx", (double) syncTime / concurrentTime) + " faster");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("7. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Thread-safe cache
        System.out.println("Use Case 1: Thread-Safe Cache");
        ConcurrentHashMap<String, String> cache = new ConcurrentHashMap<>();

        String value = cache.computeIfAbsent("user:123", key -> {
            System.out.println("  Cache miss - fetching from database...");
            return "User Data for 123";
        });
        System.out.println("  Result: " + value);

        value = cache.computeIfAbsent("user:123", key -> {
            System.out.println("  This won't be called");
            return "New Data";
        });
        System.out.println("  Result (cached): " + value);

        // Use Case 2: Concurrent counter
        System.out.println("\nUse Case 2: Concurrent Counter");
        ConcurrentHashMap<String, AtomicInteger> counters = new ConcurrentHashMap<>();

        String[] events = { "login", "logout", "login", "click", "login", "logout" };
        for (String event : events) {
            counters.computeIfAbsent(event, k -> new AtomicInteger(0))
                    .incrementAndGet();
        }

        counters.forEach((event, count) -> System.out.println("  " + event + ": " + count));

        // Use Case 3: Concurrent frequency map
        System.out.println("\nUse Case 3: Word Frequency Counter");
        ConcurrentHashMap<String, Integer> wordCount = new ConcurrentHashMap<>();
        String[] words = { "hello", "world", "hello", "java", "world", "hello" };

        for (String word : words) {
            wordCount.merge(word, 1, Integer::sum);
        }

        wordCount.forEach((word, count) -> System.out.println("  " + word + ": " + count));

        System.out.println();
    }

    private static void demonstrateBestPractices() {
        System.out.println("8. BEST PRACTICES");
        System.out.println("-----------------");

        ConcurrentHashMap<String, Integer> map = new ConcurrentHashMap<>();

        System.out.println("✓ DO: Use atomic operations for compound actions");
        System.out.println("  map.computeIfAbsent(key, k -> expensiveOperation());");

        System.out.println("\n✗ DON'T: Use separate contains and put");
        System.out.println("  if (!map.containsKey(key)) { map.put(key, value); } // NOT ATOMIC!");

        System.out.println("\n✓ DO: Use merge for accumulation");
        System.out.println("  map.merge(key, 1, Integer::sum);");

        System.out.println("\n✗ DON'T: Use null keys or values");
        System.out.println("  map.put(null, value); // Throws NullPointerException");

        System.out.println("\n✓ DO: Use bulk operations for better performance");
        System.out.println("  map.forEach(parallelismThreshold, action);");

        System.out.println("\n✓ DO: Size is approximate during concurrent modifications");
        System.out.println("  long count = map.mappingCount(); // More accurate than size()");

        System.out.println("\n✓ DO: Iterators are weakly consistent");
        System.out.println("  for (Entry<K,V> e : map.entrySet()) { ... } // Safe during modifications");

        System.out.println("\n=== End of ConcurrentHashMap Example ===");
    }
}
