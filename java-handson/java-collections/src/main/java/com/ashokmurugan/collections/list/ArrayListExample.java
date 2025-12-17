package com.ashokmurugan.collections.list;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Collections;

/**
 * ArrayList Example - Dynamic Array Implementation
 * 
 * EXPLANATION:
 * ArrayList is a resizable array implementation of the List interface.
 * It provides dynamic array functionality with automatic resizing.
 * Elements are stored in a contiguous memory block (internally uses Object[]).
 * 
 * KEY CHARACTERISTICS:
 * - Implements List, RandomAccess, Cloneable, Serializable
 * - Allows duplicate elements
 * - Maintains insertion order
 * - Not synchronized (not thread-safe)
 * - Allows null elements
 * - Fast random access via index
 * 
 * INTERNAL STRUCTURE:
 * - Uses Object[] array internally
 * - Default initial capacity: 10
 * - Growth factor: 1.5x (newCapacity = oldCapacity + (oldCapacity >> 1))
 * 
 * TIME COMPLEXITY:
 * - add(E e)           : O(1) amortized, O(n) worst case (when resize needed)
 * - add(int index, E)  : O(n) - needs to shift elements
 * - get(int index)     : O(1) - direct array access
 * - set(int index, E)  : O(1) - direct array access
 * - remove(int index)  : O(n) - needs to shift elements
 * - remove(Object o)   : O(n) - needs to search and shift
 * - contains(Object o) : O(n) - linear search
 * - indexOf(Object o)  : O(n) - linear search
 * - clear()            : O(n) - sets all elements to null
 * - size()             : O(1) - maintains size variable
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of elements
 * 
 * WHEN TO USE:
 * ✓ Frequent random access by index
 * ✓ Iteration over elements
 * ✓ Adding elements at the end
 * ✗ Frequent insertions/deletions in the middle
 * ✗ Thread-safe operations (use Vector or Collections.synchronizedList)
 */
public class ArrayListExample {
    
    public static void main(String[] args) {
        System.out.println("=== ArrayList Comprehensive Example ===\n");
        
        // 1. Creation and Initialization
        demonstrateCreation();
        
        // 2. Basic Operations
        demonstrateBasicOperations();
        
        // 3. Bulk Operations
        demonstrateBulkOperations();
        
        // 4. Iteration Methods
        demonstrateIteration();
        
        // 5. Search Operations
        demonstrateSearchOperations();
        
        // 6. Sorting and Manipulation
        demonstrateSortingAndManipulation();
        
        // 7. Performance Characteristics
        demonstratePerformance();
        
        // 8. Edge Cases
        demonstrateEdgeCases();
    }
    
    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");
        
        // Default constructor - initial capacity 10
        ArrayList<String> list1 = new ArrayList<>();
        System.out.println("Empty ArrayList: " + list1);
        
        // Constructor with initial capacity
        ArrayList<Integer> list2 = new ArrayList<>(20);
        System.out.println("ArrayList with capacity 20: " + list2);
        
        // Constructor with collection
        List<String> sourceList = List.of("A", "B", "C");
        ArrayList<String> list3 = new ArrayList<>(sourceList);
        System.out.println("ArrayList from collection: " + list3);
        
        // Using List.of() (immutable) vs ArrayList (mutable)
        List<String> immutable = List.of("X", "Y", "Z");
        ArrayList<String> mutable = new ArrayList<>(immutable);
        System.out.println("Mutable copy: " + mutable);
        
        System.out.println();
    }
    
    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");
        
        ArrayList<String> fruits = new ArrayList<>();
        
        // Adding elements - O(1) amortized
        fruits.add("Apple");
        fruits.add("Banana");
        fruits.add("Cherry");
        fruits.add("Date");
        System.out.println("After adding: " + fruits);
        
        // Adding at specific index - O(n)
        fruits.add(1, "Avocado");
        System.out.println("After add at index 1: " + fruits);
        
        // Getting element - O(1)
        String fruit = fruits.get(2);
        System.out.println("Element at index 2: " + fruit);
        
        // Setting element - O(1)
        fruits.set(0, "Apricot");
        System.out.println("After set index 0: " + fruits);
        
        // Removing by index - O(n)
        String removed = fruits.remove(1);
        System.out.println("Removed: " + removed + ", List: " + fruits);
        
        // Removing by object - O(n)
        boolean isRemoved = fruits.remove("Cherry");
        System.out.println("Removed Cherry: " + isRemoved + ", List: " + fruits);
        
        // Size - O(1)
        System.out.println("Size: " + fruits.size());
        
        // isEmpty - O(1)
        System.out.println("Is empty: " + fruits.isEmpty());
        
        System.out.println();
    }
    
    private static void demonstrateBulkOperations() {
        System.out.println("3. BULK OPERATIONS");
        System.out.println("------------------");
        
        ArrayList<Integer> numbers = new ArrayList<>(List.of(1, 2, 3, 4, 5));
        System.out.println("Original: " + numbers);
        
        // addAll - O(n) where n is size of collection being added
        ArrayList<Integer> moreNumbers = new ArrayList<>(List.of(6, 7, 8));
        numbers.addAll(moreNumbers);
        System.out.println("After addAll: " + numbers);
        
        // addAll at index - O(n + m)
        numbers.addAll(0, List.of(-1, 0));
        System.out.println("After addAll at index 0: " + numbers);
        
        // removeAll - O(n * m) where m is size of collection
        numbers.removeAll(List.of(0, 5, 10));
        System.out.println("After removeAll [0,5,10]: " + numbers);
        
        // retainAll - O(n * m)
        ArrayList<Integer> toRetain = new ArrayList<>(List.of(1, 2, 3, 4, 5, 6));
        numbers.retainAll(toRetain);
        System.out.println("After retainAll [1-6]: " + numbers);
        
        // containsAll - O(n * m)
        boolean hasAll = numbers.containsAll(List.of(1, 2, 3));
        System.out.println("Contains [1,2,3]: " + hasAll);
        
        // clear - O(n)
        ArrayList<Integer> temp = new ArrayList<>(numbers);
        temp.clear();
        System.out.println("After clear: " + temp);
        
        System.out.println();
    }
    
    private static void demonstrateIteration() {
        System.out.println("4. ITERATION METHODS");
        System.out.println("--------------------");
        
        ArrayList<String> colors = new ArrayList<>(List.of("Red", "Green", "Blue", "Yellow"));
        
        // 1. Traditional for loop - Best for index-based access
        System.out.print("For loop: ");
        for (int i = 0; i < colors.size(); i++) {
            System.out.print(colors.get(i) + " ");
        }
        System.out.println();
        
        // 2. Enhanced for loop - Clean and readable
        System.out.print("Enhanced for: ");
        for (String color : colors) {
            System.out.print(color + " ");
        }
        System.out.println();
        
        // 3. Iterator - Safe for removal during iteration
        System.out.print("Iterator: ");
        Iterator<String> iterator = colors.iterator();
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();
        
        // 4. forEach with lambda - Functional style
        System.out.print("forEach lambda: ");
        colors.forEach(color -> System.out.print(color + " "));
        System.out.println();
        
        // 5. Stream API - For complex operations
        System.out.print("Stream: ");
        colors.stream()
              .filter(c -> c.length() > 3)
              .forEach(c -> System.out.print(c + " "));
        System.out.println("\n");
    }
    
    private static void demonstrateSearchOperations() {
        System.out.println("5. SEARCH OPERATIONS");
        System.out.println("--------------------");
        
        ArrayList<String> animals = new ArrayList<>(
            List.of("Cat", "Dog", "Elephant", "Dog", "Fox", "Dog")
        );
        System.out.println("List: " + animals);
        
        // contains - O(n)
        boolean hasDog = animals.contains("Dog");
        System.out.println("Contains 'Dog': " + hasDog);
        
        // indexOf - O(n) - first occurrence
        int firstDog = animals.indexOf("Dog");
        System.out.println("First index of 'Dog': " + firstDog);
        
        // lastIndexOf - O(n) - last occurrence
        int lastDog = animals.lastIndexOf("Dog");
        System.out.println("Last index of 'Dog': " + lastDog);
        
        // indexOf for non-existent element
        int lion = animals.indexOf("Lion");
        System.out.println("Index of 'Lion': " + lion + " (not found)");
        
        System.out.println();
    }
    
    private static void demonstrateSortingAndManipulation() {
        System.out.println("6. SORTING AND MANIPULATION");
        System.out.println("---------------------------");
        
        ArrayList<Integer> numbers = new ArrayList<>(List.of(5, 2, 8, 1, 9, 3));
        System.out.println("Original: " + numbers);
        
        // Sort - O(n log n)
        Collections.sort(numbers);
        System.out.println("After sort: " + numbers);
        
        // Reverse - O(n)
        Collections.reverse(numbers);
        System.out.println("After reverse: " + numbers);
        
        // Shuffle - O(n)
        Collections.shuffle(numbers);
        System.out.println("After shuffle: " + numbers);
        
        // Sort with custom comparator
        numbers.sort((a, b) -> b - a); // Descending order
        System.out.println("Descending sort: " + numbers);
        
        // SubList - O(1) - returns view, not copy
        List<Integer> subList = numbers.subList(1, 4);
        System.out.println("SubList [1,4): " + subList);
        
        // toArray - O(n)
        Integer[] array = numbers.toArray(new Integer[0]);
        System.out.print("To array: ");
        for (Integer num : array) {
            System.out.print(num + " ");
        }
        System.out.println("\n");
    }
    
    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");
        
        ArrayList<Integer> list = new ArrayList<>();
        
        // Adding at end - O(1) amortized
        long start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            list.add(i);
        }
        long end = System.nanoTime();
        System.out.println("Add 10,000 elements at end: " + (end - start) / 1000 + " μs");
        
        // Random access - O(1)
        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            int val = list.get(i);
        }
        end = System.nanoTime();
        System.out.println("Get 10,000 elements: " + (end - start) / 1000 + " μs");
        
        // Adding at beginning - O(n) - expensive!
        ArrayList<Integer> list2 = new ArrayList<>();
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            list2.add(0, i); // Adds at beginning
        }
        end = System.nanoTime();
        System.out.println("Add 1,000 elements at beginning: " + (end - start) / 1000 + " μs (SLOW)");
        
        System.out.println();
    }
    
    private static void demonstrateEdgeCases() {
        System.out.println("8. EDGE CASES AND SPECIAL SCENARIOS");
        System.out.println("------------------------------------");
        
        ArrayList<String> list = new ArrayList<>();
        
        // Null elements are allowed
        list.add(null);
        list.add("A");
        list.add(null);
        list.add("B");
        System.out.println("List with nulls: " + list);
        
        // Duplicate elements are allowed
        ArrayList<String> duplicates = new ArrayList<>(List.of("A", "A", "B", "A"));
        System.out.println("List with duplicates: " + duplicates);
        
        // ensureCapacity - optimize if you know size beforehand
        ArrayList<Integer> optimized = new ArrayList<>();
        optimized.ensureCapacity(10000); // Prevents multiple resizes
        System.out.println("Ensured capacity of 10,000");
        
        // trimToSize - reduce memory footprint
        ArrayList<Integer> large = new ArrayList<>(10000);
        large.add(1);
        large.add(2);
        large.trimToSize(); // Reduces capacity to match size
        System.out.println("Trimmed to size: " + large.size());
        
        // Clone - shallow copy
        ArrayList<String> original = new ArrayList<>(List.of("X", "Y", "Z"));
        @SuppressWarnings("unchecked")
        ArrayList<String> cloned = (ArrayList<String>) original.clone();
        cloned.add("W");
        System.out.println("Original: " + original);
        System.out.println("Cloned: " + cloned);
        
        System.out.println("\n=== End of ArrayList Example ===");
    }
}
