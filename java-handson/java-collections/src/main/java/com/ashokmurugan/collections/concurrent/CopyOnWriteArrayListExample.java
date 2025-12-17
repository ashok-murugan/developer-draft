package com.ashokmurugan.collections.concurrent;

import java.util.concurrent.CopyOnWriteArrayList;
import java.util.List;
import java.util.ArrayList;
import java.util.Iterator;

/**
 * CopyOnWriteArrayList Example - Thread-Safe List with Copy-On-Write Semantics
 * 
 * EXPLANATION:
 * CopyOnWriteArrayList is a thread-safe variant of ArrayList where all mutative
 * operations
 * (add, set, remove) are implemented by making a fresh copy of the underlying
 * array.
 * Optimized for scenarios where reads vastly outnumber writes.
 * 
 * KEY CHARACTERISTICS:
 * - Implements List, RandomAccess, Cloneable, Serializable
 * - Thread-safe without synchronization on reads
 * - All mutative operations create a new copy of the array
 * - Iterators are snapshot-based (never throw ConcurrentModificationException)
 * - Allows null elements
 * - Memory intensive (creates copy on every write)
 * 
 * INTERNAL STRUCTURE:
 * - Uses volatile Object[] array
 * - ReentrantLock for write operations
 * - Reads are lock-free (volatile read)
 * - Writes create new array copy
 * 
 * COPY-ON-WRITE MECHANISM:
 * 1. Lock acquired for write operation
 * 2. Current array copied to new array
 * 3. Modification applied to new array
 * 4. Volatile write to replace old array with new
 * 5. Lock released
 * 
 * TIME COMPLEXITY:
 * - get(index) : O(1) - lock-free read
 * - add(E) : O(n) - copies entire array
 * - add(index, E) : O(n) - copies entire array
 * - set(index, E) : O(n) - copies entire array
 * - remove(index) : O(n) - copies entire array
 * - contains(E) : O(n) - linear search
 * - iterator() : O(1) - returns snapshot iterator
 * - size() : O(1) - array length
 * 
 * SPACE COMPLEXITY: O(n) + O(n) during write (temporary copy)
 * 
 * WHEN TO USE:
 * ✓ Read operations vastly outnumber writes
 * ✓ Need thread-safe iteration without locking
 * ✓ Iterator consistency more important than real-time updates
 * ✓ Small to medium-sized lists
 * ✗ Frequent modifications (very expensive)
 * ✗ Large lists (memory overhead)
 * ✗ Need real-time consistency
 * 
 * COPYONWRITEARRAYLIST vs SYNCHRONIZEDLIST vs VECTOR:
 * - CopyOnWriteArrayList: Best for read-heavy, lock-free reads, snapshot
 * iterators
 * - Collections.synchronizedList: Balanced read/write, synchronized on all
 * operations
 * - Vector: Legacy, synchronized on all operations, fail-fast iterators
 */
public class CopyOnWriteArrayListExample {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== CopyOnWriteArrayList Comprehensive Example ===\n");

        // 1. Creation and Basic Operations
        demonstrateCreation();

        // 2. Thread-Safe Reads
        demonstrateThreadSafeReads();

        // 3. Copy-On-Write Mechanism
        demonstrateCopyOnWrite();

        // 4. Snapshot Iterators
        demonstrateSnapshotIterators();

        // 5. Concurrent Iteration and Modification
        demonstrateConcurrentModification();

        // 6. Performance Characteristics
        demonstratePerformance();

        // 7. Practical Use Cases
        demonstratePracticalUseCases();

        // 8. Best Practices
        demonstrateBestPractices();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND BASIC OPERATIONS");
        System.out.println("---------------------------------");

        // Default constructor
        CopyOnWriteArrayList<String> list1 = new CopyOnWriteArrayList<>();
        System.out.println("Empty CopyOnWriteArrayList: " + list1);

        // Constructor with collection
        List<Integer> source = List.of(1, 2, 3, 4, 5);
        CopyOnWriteArrayList<Integer> list2 = new CopyOnWriteArrayList<>(source);
        System.out.println("From collection: " + list2);

        // Constructor with array
        String[] array = { "A", "B", "C" };
        CopyOnWriteArrayList<String> list3 = new CopyOnWriteArrayList<>(array);
        System.out.println("From array: " + list3);

        // Basic operations
        list1.add("Apple");
        list1.add("Banana");
        list1.add("Cherry");
        System.out.println("\nAfter adding: " + list1);

        // Get - O(1), lock-free
        String fruit = list1.get(1);
        System.out.println("Element at index 1: " + fruit);

        // Set - O(n), creates new array
        list1.set(0, "Apricot");
        System.out.println("After set: " + list1);

        // Remove - O(n), creates new array
        list1.remove(1);
        System.out.println("After remove: " + list1);

        System.out.println();
    }

    private static void demonstrateThreadSafeReads() throws InterruptedException {
        System.out.println("2. THREAD-SAFE READS");
        System.out.println("---------------------");

        CopyOnWriteArrayList<Integer> list = new CopyOnWriteArrayList<>();

        // Populate list
        for (int i = 0; i < 100; i++) {
            list.add(i);
        }

        System.out.println("Initial size: " + list.size());

        // Multiple concurrent readers (lock-free)
        Thread[] readers = new Thread[10];
        long[] readCounts = new long[10];

        long start = System.nanoTime();

        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            readers[i] = new Thread(() -> {
                for (int j = 0; j < 10000; j++) {
                    int index = j % list.size();
                    Integer value = list.get(index);
                    readCounts[threadId]++;
                }
            });
            readers[i].start();
        }

        for (Thread t : readers) {
            t.join();
        }

        long end = System.nanoTime();

        long totalReads = 0;
        for (long count : readCounts) {
            totalReads += count;
        }

        System.out.println("Total reads: " + totalReads);
        System.out.println("Time taken: " + (end - start) / 1000000 + " ms");
        System.out.println("All reads completed successfully (lock-free)");

        System.out.println();
    }

    private static void demonstrateCopyOnWrite() {
        System.out.println("3. COPY-ON-WRITE MECHANISM");
        System.out.println("--------------------------");

        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
        list.add("A");
        list.add("B");
        list.add("C");

        System.out.println("Original list: " + list);
        System.out.println("List identity: " + System.identityHashCode(list));

        // Get reference to internal array (conceptually)
        System.out.println("\nBefore modification:");
        System.out.println("  Size: " + list.size());

        // Modification creates new array copy
        System.out.println("\nAdding element 'D'...");
        System.out.println("  1. Lock acquired");
        System.out.println("  2. Current array [A, B, C] copied to new array");
        System.out.println("  3. 'D' added to new array [A, B, C, D]");
        System.out.println("  4. Internal reference updated to new array");
        System.out.println("  5. Lock released");

        list.add("D");

        System.out.println("\nAfter modification:");
        System.out.println("  List: " + list);
        System.out.println("  Size: " + list.size());
        System.out.println("  List identity: " + System.identityHashCode(list) + " (same object)");
        System.out.println("  Internal array: NEW (different array)");

        System.out.println();
    }

    private static void demonstrateSnapshotIterators() {
        System.out.println("4. SNAPSHOT ITERATORS");
        System.out.println("---------------------");

        CopyOnWriteArrayList<String> list = new CopyOnWriteArrayList<>();
        list.add("One");
        list.add("Two");
        list.add("Three");

        System.out.println("Original list: " + list);

        // Get iterator (creates snapshot)
        Iterator<String> iterator = list.iterator();
        System.out.println("\nIterator created (snapshot of current state)");

        // Modify list after iterator creation
        list.add("Four");
        list.add("Five");
        System.out.println("Added 'Four' and 'Five' to list");
        System.out.println("Current list: " + list);

        // Iterator still sees old snapshot
        System.out.print("\nIterator sees: ");
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println("(snapshot from creation time)");

        // New iterator sees current state
        System.out.print("New iterator sees: ");
        for (String s : list) {
            System.out.print(s + " ");
        }
        System.out.println("(current state)");

        // Iterator.remove() not supported
        System.out.println("\nNote: Iterator.remove() throws UnsupportedOperationException");

        System.out.println();
    }

    private static void demonstrateConcurrentModification() throws InterruptedException {
        System.out.println("5. CONCURRENT ITERATION AND MODIFICATION");
        System.out.println("-----------------------------------------");

        CopyOnWriteArrayList<Integer> cowList = new CopyOnWriteArrayList<>();
        List<Integer> syncList = java.util.Collections.synchronizedList(new ArrayList<>());

        // Populate both lists
        for (int i = 0; i < 100; i++) {
            cowList.add(i);
            syncList.add(i);
        }

        // Test CopyOnWriteArrayList
        System.out.println("Testing CopyOnWriteArrayList:");
        Thread cowReader = new Thread(() -> {
            int count = 0;
            for (Integer num : cowList) {
                count++;
                try {
                    Thread.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            System.out.println("  Reader: Iterated " + count + " elements (no exception)");
        });

        Thread cowWriter = new Thread(() -> {
            for (int i = 100; i < 150; i++) {
                cowList.add(i);
                try {
                    Thread.sleep(1);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
            System.out.println("  Writer: Added 50 elements");
        });

        cowReader.start();
        cowWriter.start();
        cowReader.join();
        cowWriter.join();

        System.out.println("  Final size: " + cowList.size());
        System.out.println("  ✓ No ConcurrentModificationException");

        // Test synchronized list (would throw exception without synchronization)
        System.out.println("\nTesting synchronized ArrayList:");
        System.out.println("  Requires manual synchronization for iteration");
        System.out.println("  synchronized(list) { for(E e : list) {...} }");

        System.out.println();
    }

    private static void demonstratePerformance() throws InterruptedException {
        System.out.println("6. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        int size = 1000;

        // Read performance
        CopyOnWriteArrayList<Integer> cowList = new CopyOnWriteArrayList<>();
        List<Integer> syncList = java.util.Collections.synchronizedList(new ArrayList<>());

        for (int i = 0; i < size; i++) {
            cowList.add(i);
            syncList.add(i);
        }

        // CopyOnWriteArrayList reads (lock-free)
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            int val = cowList.get(i % size);
        }
        long cowReadTime = (System.nanoTime() - start) / 1000000;
        System.out.println("CopyOnWriteArrayList - 100,000 reads: " + cowReadTime + " ms (lock-free)");

        // Synchronized list reads (synchronized)
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            int val = syncList.get(i % size);
        }
        long syncReadTime = (System.nanoTime() - start) / 1000000;
        System.out.println("SynchronizedList - 100,000 reads: " + syncReadTime + " ms (synchronized)");

        System.out.println("Read speedup: " + String.format("%.2fx", (double) syncReadTime / cowReadTime));

        // Write performance
        CopyOnWriteArrayList<Integer> cowList2 = new CopyOnWriteArrayList<>();
        List<Integer> syncList2 = java.util.Collections.synchronizedList(new ArrayList<>());

        // CopyOnWriteArrayList writes (expensive - copies array)
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            cowList2.add(i);
        }
        long cowWriteTime = (System.nanoTime() - start) / 1000000;
        System.out.println("\nCopyOnWriteArrayList - 1,000 adds: " + cowWriteTime + " ms (copies array)");

        // Synchronized list writes
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            syncList2.add(i);
        }
        long syncWriteTime = (System.nanoTime() - start) / 1000000;
        System.out.println("SynchronizedList - 1,000 adds: " + syncWriteTime + " ms");

        System.out.println("Write slowdown: " + String.format("%.2fx", (double) cowWriteTime / syncWriteTime));

        System.out.println("\n⚠ CopyOnWriteArrayList: Fast reads, slow writes");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("7. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Event listeners
        System.out.println("Use Case 1: Event Listeners (read-heavy)");
        CopyOnWriteArrayList<String> listeners = new CopyOnWriteArrayList<>();

        listeners.add("LoggingListener");
        listeners.add("MetricsListener");
        listeners.add("AlertListener");

        System.out.println("  Registered listeners: " + listeners);
        System.out.println("  Notifying all listeners (frequent reads):");
        for (String listener : listeners) {
            System.out.println("    Notifying: " + listener);
        }

        // Use Case 2: Configuration values
        System.out.println("\nUse Case 2: Configuration Cache (rarely updated)");
        CopyOnWriteArrayList<String> config = new CopyOnWriteArrayList<>();
        config.add("server.port=8080");
        config.add("server.host=localhost");
        config.add("db.url=jdbc:mysql://localhost:3306");

        System.out.println("  Config values: " + config.size());
        System.out.println("  Read frequently, updated rarely");

        // Use Case 3: Whitelist/Blacklist
        System.out.println("\nUse Case 3: IP Whitelist (read on every request)");
        CopyOnWriteArrayList<String> whitelist = new CopyOnWriteArrayList<>();
        whitelist.add("192.168.1.1");
        whitelist.add("192.168.1.2");
        whitelist.add("10.0.0.1");

        String clientIp = "192.168.1.1";
        boolean allowed = whitelist.contains(clientIp);
        System.out.println("  Client IP " + clientIp + " allowed: " + allowed);
        System.out.println("  Checked on every request (frequent reads)");
        System.out.println("  Updated occasionally by admin (rare writes)");

        System.out.println();
    }

    private static void demonstrateBestPractices() {
        System.out.println("8. BEST PRACTICES");
        System.out.println("-----------------");

        System.out.println("✓ DO: Use for read-heavy scenarios");
        System.out.println("  - Event listeners");
        System.out.println("  - Configuration caches");
        System.out.println("  - Whitelists/blacklists");

        System.out.println("\n✗ DON'T: Use for write-heavy scenarios");
        System.out.println("  - Frequent additions/removals");
        System.out.println("  - Large lists (memory overhead)");

        System.out.println("\n✓ DO: Use when iteration consistency is important");
        System.out.println("  - Snapshot iterators never throw ConcurrentModificationException");

        System.out.println("\n✓ DO: Consider for small to medium lists");
        System.out.println("  - Array copy overhead acceptable for small lists");

        System.out.println("\n✗ DON'T: Expect real-time updates in iterators");
        System.out.println("  - Iterators see snapshot from creation time");

        System.out.println("\n✓ DO: Use addAll() for bulk additions");
        System.out.println("  - Single array copy instead of multiple");

        System.out.println("\nRule of thumb:");
        System.out.println("  Use if: reads >> writes (100:1 or better)");
        System.out.println("  Otherwise: Use Collections.synchronizedList()");

        System.out.println("\n=== End of CopyOnWriteArrayList Example ===");
    }
}
