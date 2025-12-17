package com.ashokmurugan.collections.list;

import java.util.Vector;
import java.util.List;
import java.util.Enumeration;

/**
 * Vector Example - Synchronized Dynamic Array Implementation
 * 
 * EXPLANATION:
 * Vector is a legacy synchronized implementation of List interface (since Java
 * 1.0).
 * Similar to ArrayList but all methods are synchronized, making it thread-safe.
 * Generally slower than ArrayList due to synchronization overhead.
 * 
 * KEY CHARACTERISTICS:
 * - Implements List, RandomAccess, Cloneable, Serializable
 * - Synchronized (thread-safe) - all methods are synchronized
 * - Allows duplicate elements
 * - Maintains insertion order
 * - Allows null elements
 * - Fast random access via index
 * - Legacy class (prefer ArrayList with external synchronization)
 * 
 * INTERNAL STRUCTURE:
 * - Uses Object[] array internally (like ArrayList)
 * - Default initial capacity: 10
 * - Growth factor: 2x (doubles capacity) or custom capacityIncrement
 * - Different from ArrayList which grows by 1.5x
 * 
 * TIME COMPLEXITY:
 * - add(E e) : O(1) amortized, O(n) worst case (when resize needed)
 * - add(int index, E) : O(n) - needs to shift elements
 * - get(int index) : O(1) - direct array access
 * - set(int index, E) : O(1) - direct array access
 * - remove(int index) : O(n) - needs to shift elements
 * - remove(Object o) : O(n) - needs to search and shift
 * - contains(Object o) : O(n) - linear search
 * - size() : O(1)
 * 
 * Note: All operations have additional synchronization overhead
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of elements
 * 
 * WHEN TO USE:
 * ✓ Legacy code compatibility
 * ✓ Need thread-safe list (though Collections.synchronizedList(ArrayList) is
 * preferred)
 * ✗ Modern applications (use ArrayList instead)
 * ✗ Performance-critical code (synchronization overhead)
 * ✗ Single-threaded applications (unnecessary overhead)
 * 
 * VECTOR vs ARRAYLIST:
 * - Vector: Synchronized, thread-safe, grows by 2x, legacy
 * - ArrayList: Not synchronized, faster, grows by 1.5x, modern
 */
public class VectorExample {

    public static void main(String[] args) {
        System.out.println("=== Vector Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Basic Operations
        demonstrateBasicOperations();

        // 3. Vector-Specific Methods
        demonstrateVectorSpecificMethods();

        // 4. Enumeration (Legacy Iterator)
        demonstrateEnumeration();

        // 5. Thread Safety
        demonstrateThreadSafety();

        // 6. Capacity Management
        demonstrateCapacityManagement();

        // 7. Vector vs ArrayList Performance
        demonstratePerformanceComparison();

        // 8. When to Use Vector
        demonstrateUseCases();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor - capacity 10
        Vector<String> vec1 = new Vector<>();
        System.out.println("Empty Vector: " + vec1);

        // Constructor with initial capacity
        Vector<Integer> vec2 = new Vector<>(20);
        System.out.println("Vector with capacity 20: " + vec2);

        // Constructor with capacity and increment
        Vector<String> vec3 = new Vector<>(10, 5);
        System.out.println("Vector with capacity 10, increment 5: " + vec3);

        // Constructor with collection
        List<String> sourceList = List.of("A", "B", "C");
        Vector<String> vec4 = new Vector<>(sourceList);
        System.out.println("Vector from collection: " + vec4);

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");

        Vector<String> fruits = new Vector<>();

        // Adding elements - synchronized
        fruits.add("Apple");
        fruits.add("Banana");
        fruits.add("Cherry");
        System.out.println("After adding: " + fruits);

        // Adding at index
        fruits.add(1, "Avocado");
        System.out.println("After add at index 1: " + fruits);

        // Getting element
        String fruit = fruits.get(2);
        System.out.println("Element at index 2: " + fruit);

        // Setting element
        fruits.set(0, "Apricot");
        System.out.println("After set index 0: " + fruits);

        // Removing by index
        String removed = fruits.remove(1);
        System.out.println("Removed: " + removed + ", Vector: " + fruits);

        // Removing by object
        boolean isRemoved = fruits.remove("Cherry");
        System.out.println("Removed Cherry: " + isRemoved + ", Vector: " + fruits);

        // Size
        System.out.println("Size: " + fruits.size());

        // Contains
        System.out.println("Contains Banana: " + fruits.contains("Banana"));

        System.out.println();
    }

    private static void demonstrateVectorSpecificMethods() {
        System.out.println("3. VECTOR-SPECIFIC METHODS");
        System.out.println("--------------------------");

        Vector<Integer> numbers = new Vector<>();

        // addElement - legacy method (same as add)
        numbers.addElement(10);
        numbers.addElement(20);
        numbers.addElement(30);
        System.out.println("After addElement: " + numbers);

        // insertElementAt - legacy method (same as add(index, element))
        numbers.insertElementAt(15, 1);
        System.out.println("After insertElementAt(15, 1): " + numbers);

        // setElementAt - legacy method (same as set)
        numbers.setElementAt(25, 2);
        System.out.println("After setElementAt(25, 2): " + numbers);

        // elementAt - legacy method (same as get)
        Integer element = numbers.elementAt(1);
        System.out.println("elementAt(1): " + element);

        // firstElement and lastElement
        Integer first = numbers.firstElement();
        Integer last = numbers.lastElement();
        System.out.println("First: " + first + ", Last: " + last);

        // removeElement - legacy method (same as remove(Object))
        numbers.removeElement(15);
        System.out.println("After removeElement(15): " + numbers);

        // removeElementAt - legacy method (same as remove(index))
        numbers.removeElementAt(0);
        System.out.println("After removeElementAt(0): " + numbers);

        // removeAllElements - legacy method (same as clear)
        Vector<Integer> temp = new Vector<>(numbers);
        temp.removeAllElements();
        System.out.println("After removeAllElements: " + temp);

        System.out.println();
    }

    private static void demonstrateEnumeration() {
        System.out.println("4. ENUMERATION (Legacy Iterator)");
        System.out.println("---------------------------------");

        Vector<String> colors = new Vector<>(List.of("Red", "Green", "Blue", "Yellow"));

        System.out.println("Vector: " + colors);

        // Enumeration - legacy way to iterate
        System.out.print("Enumeration: ");
        Enumeration<String> enumeration = colors.elements();
        while (enumeration.hasMoreElements()) {
            System.out.print(enumeration.nextElement() + " ");
        }
        System.out.println();

        // Modern iteration methods also work
        System.out.print("Enhanced for: ");
        for (String color : colors) {
            System.out.print(color + " ");
        }
        System.out.println();

        System.out.print("forEach: ");
        colors.forEach(c -> System.out.print(c + " "));
        System.out.println("\n");
    }

    private static void demonstrateThreadSafety() {
        System.out.println("5. THREAD SAFETY");
        System.out.println("----------------");

        Vector<Integer> sharedVector = new Vector<>();

        // Vector is thread-safe - all methods are synchronized
        Thread writer1 = new Thread(() -> {
            for (int i = 0; i < 100; i++) {
                sharedVector.add(i);
            }
        });

        Thread writer2 = new Thread(() -> {
            for (int i = 100; i < 200; i++) {
                sharedVector.add(i);
            }
        });

        try {
            writer1.start();
            writer2.start();
            writer1.join();
            writer2.join();

            System.out.println("Vector size after concurrent writes: " + sharedVector.size());
            System.out.println("Expected: 200, Actual: " + sharedVector.size());
            System.out.println("Thread-safe: " + (sharedVector.size() == 200));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        System.out.println("\nNote: While individual operations are thread-safe,");
        System.out.println("compound operations still need external synchronization:");
        System.out.println("  // NOT thread-safe:");
        System.out.println("  if (!vector.isEmpty()) {");
        System.out.println("      vector.remove(0); // Another thread might empty it!");
        System.out.println("  }");
        System.out.println("\n  // Thread-safe:");
        System.out.println("  synchronized(vector) {");
        System.out.println("      if (!vector.isEmpty()) {");
        System.out.println("          vector.remove(0);");
        System.out.println("      }");
        System.out.println("  }");

        System.out.println();
    }

    private static void demonstrateCapacityManagement() {
        System.out.println("6. CAPACITY MANAGEMENT");
        System.out.println("----------------------");

        // Vector with default capacity (10) and default increment (doubles)
        Vector<Integer> vec1 = new Vector<>();
        System.out.println("Initial capacity: " + vec1.capacity());

        for (int i = 0; i < 11; i++) {
            vec1.add(i);
        }
        System.out.println("After adding 11 elements, capacity: " + vec1.capacity());
        System.out.println("(Doubled from 10 to 20)");

        // Vector with custom capacity increment
        Vector<Integer> vec2 = new Vector<>(10, 5);
        System.out.println("\nVector with increment 5, initial capacity: " + vec2.capacity());

        for (int i = 0; i < 11; i++) {
            vec2.add(i);
        }
        System.out.println("After adding 11 elements, capacity: " + vec2.capacity());
        System.out.println("(Increased by 5, from 10 to 15)");

        // ensureCapacity
        Vector<Integer> vec3 = new Vector<>();
        vec3.ensureCapacity(100);
        System.out.println("\nAfter ensureCapacity(100): " + vec3.capacity());

        // trimToSize
        vec3.add(1);
        vec3.add(2);
        vec3.trimToSize();
        System.out.println("After trimToSize (size=2): " + vec3.capacity());

        System.out.println();
    }

    private static void demonstratePerformanceComparison() {
        System.out.println("7. VECTOR vs ARRAYLIST PERFORMANCE");
        System.out.println("-----------------------------------");

        Vector<Integer> vector = new Vector<>();
        java.util.ArrayList<Integer> arrayList = new java.util.ArrayList<>();

        // Vector - synchronized overhead
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            vector.add(i);
        }
        long end = System.nanoTime();
        long vectorTime = (end - start) / 1000000;
        System.out.println("Vector - Add 100,000: " + vectorTime + " ms");

        // ArrayList - no synchronization
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            arrayList.add(i);
        }
        end = System.nanoTime();
        long arrayListTime = (end - start) / 1000000;
        System.out.println("ArrayList - Add 100,000: " + arrayListTime + " ms");

        System.out.println("\nArrayList is faster due to no synchronization overhead");
        System.out.println("Speedup: " + String.format("%.2fx", (double) vectorTime / arrayListTime));

        System.out.println();
    }

    private static void demonstrateUseCases() {
        System.out.println("8. WHEN TO USE VECTOR");
        System.out.println("---------------------");

        System.out.println("LEGACY REASONS:");
        System.out.println("✓ Maintaining compatibility with old code");
        System.out.println("✓ Working with legacy APIs that require Vector");
        System.out.println();

        System.out.println("MODERN ALTERNATIVES:");
        System.out.println("Instead of Vector, use:");
        System.out.println();

        System.out.println("1. For single-threaded applications:");
        System.out.println("   ArrayList<E> list = new ArrayList<>();");
        System.out.println();

        System.out.println("2. For thread-safe list:");
        System.out.println("   List<E> list = Collections.synchronizedList(new ArrayList<>());");
        System.out.println();

        System.out.println("3. For concurrent access:");
        System.out.println("   CopyOnWriteArrayList<E> list = new CopyOnWriteArrayList<>();");
        System.out.println();

        System.out.println("RECOMMENDATION:");
        System.out.println("Vector is a legacy class. For new code:");
        System.out.println("- Use ArrayList for better performance");
        System.out.println("- Use Collections.synchronizedList() if thread-safety needed");
        System.out.println("- Use CopyOnWriteArrayList for concurrent read-heavy scenarios");

        System.out.println("\n=== End of Vector Example ===");
    }
}
