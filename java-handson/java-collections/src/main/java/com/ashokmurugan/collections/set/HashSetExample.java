package com.ashokmurugan.collections.set;

import java.util.HashSet;
import java.util.Set;
import java.util.Iterator;
import java.util.Arrays;

/**
 * HashSet Example - Hash Table Based Set Implementation
 * 
 * EXPLANATION:
 * HashSet is a hash table based implementation of the Set interface.
 * It uses a HashMap internally to store elements (elements are keys, with a
 * dummy value).
 * Does not allow duplicate elements and does not maintain any order.
 * 
 * KEY CHARACTERISTICS:
 * - Implements Set, Cloneable, Serializable
 * - No duplicate elements allowed
 * - No guaranteed order (not insertion order, not sorted)
 * - Allows one null element
 * - Not synchronized (not thread-safe)
 * - Best performance for basic operations (add, remove, contains)
 * 
 * INTERNAL STRUCTURE:
 * - Uses HashMap<E, Object> internally
 * - Elements are stored as keys in the HashMap
 * - All keys map to the same dummy Object (PRESENT)
 * - Default initial capacity: 16
 * - Default load factor: 0.75
 * - Resizes when: size > capacity * loadFactor
 * 
 * HASH FUNCTION:
 * - Uses hashCode() method of elements
 * - Good hashCode() implementation is crucial for performance
 * - Poor hashCode() can degrade performance to O(n)
 * 
 * TIME COMPLEXITY (assuming good hash function):
 * - add(E e) : O(1) average, O(n) worst case
 * - remove(Object o) : O(1) average, O(n) worst case
 * - contains(Object o) : O(1) average, O(n) worst case
 * - size() : O(1)
 * - isEmpty() : O(1)
 * - clear() : O(n)
 * - iterator() : O(capacity + size) for full iteration
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of elements
 * 
 * WHEN TO USE:
 * ✓ Need to store unique elements
 * ✓ Fast lookup/insertion/deletion required
 * ✓ Order doesn't matter
 * ✓ Implementing mathematical set operations (union, intersection, difference)
 * ✗ Need to maintain insertion order (use LinkedHashSet)
 * ✗ Need sorted order (use TreeSet)
 * ✗ Thread-safe operations (use Collections.synchronizedSet or
 * ConcurrentHashMap.newKeySet())
 */
public class HashSetExample {

    public static void main(String[] args) {
        System.out.println("=== HashSet Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Basic Operations
        demonstrateBasicOperations();

        // 3. Set Operations (Mathematical)
        demonstrateSetOperations();

        // 4. Iteration Methods
        demonstrateIteration();

        // 5. Null Handling
        demonstrateNullHandling();

        // 6. HashCode and Equals
        demonstrateHashCodeEquals();

        // 7. Performance Characteristics
        demonstratePerformance();

        // 8. Practical Use Cases
        demonstratePracticalUseCases();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor - capacity 16, load factor 0.75
        HashSet<String> set1 = new HashSet<>();
        System.out.println("Empty HashSet: " + set1);

        // Constructor with initial capacity
        HashSet<Integer> set2 = new HashSet<>(32);
        System.out.println("HashSet with capacity 32: " + set2);

        // Constructor with capacity and load factor
        HashSet<String> set3 = new HashSet<>(32, 0.8f);
        System.out.println("HashSet with capacity 32, load factor 0.8: " + set3);

        // Constructor with collection
        Set<String> sourceSet = Set.of("A", "B", "C");
        HashSet<String> set4 = new HashSet<>(sourceSet);
        System.out.println("HashSet from collection: " + set4);

        // Using Set.of() for immutable sets
        Set<Integer> immutable = Set.of(1, 2, 3, 4, 5);
        System.out.println("Immutable set: " + immutable);

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");

        HashSet<String> fruits = new HashSet<>();

        // Adding elements - O(1) average
        boolean added1 = fruits.add("Apple");
        boolean added2 = fruits.add("Banana");
        boolean added3 = fruits.add("Cherry");
        System.out.println("Added Apple: " + added1);
        System.out.println("Added Banana: " + added2);
        System.out.println("Added Cherry: " + added3);
        System.out.println("Set: " + fruits);

        // Adding duplicate - returns false
        boolean addedDuplicate = fruits.add("Apple");
        System.out.println("Added duplicate Apple: " + addedDuplicate);
        System.out.println("Set after duplicate: " + fruits + " (no change)");

        // Contains - O(1) average
        boolean hasApple = fruits.contains("Apple");
        boolean hasMango = fruits.contains("Mango");
        System.out.println("Contains Apple: " + hasApple);
        System.out.println("Contains Mango: " + hasMango);

        // Size - O(1)
        System.out.println("Size: " + fruits.size());

        // Remove - O(1) average
        boolean removed = fruits.remove("Banana");
        System.out.println("Removed Banana: " + removed);
        System.out.println("Set after removal: " + fruits);

        // isEmpty - O(1)
        System.out.println("Is empty: " + fruits.isEmpty());

        // Clear - O(n)
        fruits.clear();
        System.out.println("After clear: " + fruits);
        System.out.println("Is empty: " + fruits.isEmpty());

        System.out.println();
    }

    private static void demonstrateSetOperations() {
        System.out.println("3. SET OPERATIONS (Mathematical)");
        System.out.println("---------------------------------");

        HashSet<Integer> setA = new HashSet<>(Arrays.asList(1, 2, 3, 4, 5));
        HashSet<Integer> setB = new HashSet<>(Arrays.asList(4, 5, 6, 7, 8));

        System.out.println("Set A: " + setA);
        System.out.println("Set B: " + setB);
        System.out.println();

        // Union - A ∪ B
        HashSet<Integer> union = new HashSet<>(setA);
        union.addAll(setB);
        System.out.println("Union (A ∪ B): " + union);

        // Intersection - A ∩ B
        HashSet<Integer> intersection = new HashSet<>(setA);
        intersection.retainAll(setB);
        System.out.println("Intersection (A ∩ B): " + intersection);

        // Difference - A - B
        HashSet<Integer> difference = new HashSet<>(setA);
        difference.removeAll(setB);
        System.out.println("Difference (A - B): " + difference);

        // Symmetric Difference - (A ∪ B) - (A ∩ B)
        HashSet<Integer> symmetricDiff = new HashSet<>(setA);
        symmetricDiff.addAll(setB);
        HashSet<Integer> temp = new HashSet<>(setA);
        temp.retainAll(setB);
        symmetricDiff.removeAll(temp);
        System.out.println("Symmetric Difference: " + symmetricDiff);

        // Subset check
        HashSet<Integer> subset = new HashSet<>(Arrays.asList(1, 2, 3));
        boolean isSubset = setA.containsAll(subset);
        System.out.println(subset + " is subset of A: " + isSubset);

        // Disjoint check
        HashSet<Integer> disjoint = new HashSet<>(Arrays.asList(10, 11, 12));
        boolean areDisjoint = java.util.Collections.disjoint(setA, disjoint);
        System.out.println("A and " + disjoint + " are disjoint: " + areDisjoint);

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("4. ITERATION METHODS");
        System.out.println("--------------------");

        HashSet<String> colors = new HashSet<>(Arrays.asList("Red", "Green", "Blue", "Yellow"));

        System.out.println("Note: HashSet does NOT maintain order!");
        System.out.println("Original: " + colors);
        System.out.println();

        // 1. Enhanced for loop
        System.out.print("Enhanced for: ");
        for (String color : colors) {
            System.out.print(color + " ");
        }
        System.out.println();

        // 2. Iterator
        System.out.print("Iterator: ");
        Iterator<String> iterator = colors.iterator();
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();

        // 3. forEach with lambda
        System.out.print("forEach lambda: ");
        colors.forEach(color -> System.out.print(color + " "));
        System.out.println();

        // 4. Stream API
        System.out.print("Stream: ");
        colors.stream()
                .filter(c -> c.length() > 3)
                .forEach(c -> System.out.print(c + " "));
        System.out.println();

        // Safe removal during iteration
        System.out.println("\nRemoving elements with length > 3:");
        Iterator<String> iter = colors.iterator();
        while (iter.hasNext()) {
            String color = iter.next();
            if (color.length() > 3) {
                iter.remove();
            }
        }
        System.out.println("After removal: " + colors);

        System.out.println();
    }

    private static void demonstrateNullHandling() {
        System.out.println("5. NULL HANDLING");
        System.out.println("----------------");

        HashSet<String> set = new HashSet<>();

        // HashSet allows one null element
        set.add(null);
        set.add("A");
        set.add("B");
        System.out.println("Set with null: " + set);

        // Adding null again (duplicate)
        boolean addedNull = set.add(null);
        System.out.println("Added null again: " + addedNull);
        System.out.println("Set: " + set + " (still one null)");

        // Contains null
        boolean hasNull = set.contains(null);
        System.out.println("Contains null: " + hasNull);

        // Remove null
        boolean removedNull = set.remove(null);
        System.out.println("Removed null: " + removedNull);
        System.out.println("Set after removing null: " + set);

        System.out.println();
    }

    private static void demonstrateHashCodeEquals() {
        System.out.println("6. HASHCODE AND EQUALS");
        System.out.println("----------------------");

        // Custom class demonstrating importance of hashCode and equals
        class Person {
            String name;
            int age;

            Person(String name, int age) {
                this.name = name;
                this.age = age;
            }

            @Override
            public boolean equals(Object o) {
                if (this == o)
                    return true;
                if (o == null || getClass() != o.getClass())
                    return false;
                Person person = (Person) o;
                return age == person.age && name.equals(person.name);
            }

            @Override
            public int hashCode() {
                return java.util.Objects.hash(name, age);
            }

            @Override
            public String toString() {
                return name + "(" + age + ")";
            }
        }

        HashSet<Person> people = new HashSet<>();
        Person p1 = new Person("Alice", 30);
        Person p2 = new Person("Bob", 25);
        Person p3 = new Person("Alice", 30); // Same as p1

        people.add(p1);
        people.add(p2);
        people.add(p3); // Won't be added (duplicate)

        System.out.println("People set: " + people);
        System.out.println("Size: " + people.size() + " (p3 not added, same as p1)");

        // Contains check
        Person p4 = new Person("Alice", 30);
        boolean contains = people.contains(p4);
        System.out.println("Contains new Person('Alice', 30): " + contains);

        System.out.println("\nImportant: Always override both hashCode() and equals()!");
        System.out.println("Contract: If a.equals(b), then a.hashCode() == b.hashCode()");

        System.out.println();
    }

    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        HashSet<Integer> hashSet = new HashSet<>();

        // Adding elements - O(1) average
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            hashSet.add(i);
        }
        long end = System.nanoTime();
        System.out.println("Add 100,000 elements: " + (end - start) / 1000000 + " ms");

        // Contains check - O(1) average
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            boolean contains = hashSet.contains(i);
        }
        end = System.nanoTime();
        System.out.println("Contains check 100,000 times: " + (end - start) / 1000000 + " ms");

        // Remove elements - O(1) average
        start = System.nanoTime();
        for (int i = 0; i < 50000; i++) {
            hashSet.remove(i);
        }
        end = System.nanoTime();
        System.out.println("Remove 50,000 elements: " + (end - start) / 1000000 + " ms");

        System.out.println("\nHashSet provides constant-time performance for basic operations");
        System.out.println("Performance depends on hash function quality");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("8. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Remove duplicates from array
        Integer[] array = { 1, 2, 3, 2, 4, 5, 3, 6, 1 };
        HashSet<Integer> uniqueSet = new HashSet<>(Arrays.asList(array));
        System.out.println("Original array: " + Arrays.toString(array));
        System.out.println("Unique elements: " + uniqueSet);

        // Use Case 2: Check for duplicates
        String[] words = { "apple", "banana", "apple", "cherry" };
        HashSet<String> seen = new HashSet<>();
        System.out.print("\nDuplicates in words: ");
        for (String word : words) {
            if (!seen.add(word)) {
                System.out.print(word + " ");
            }
        }
        System.out.println();

        // Use Case 3: Fast membership test
        HashSet<String> validUsers = new HashSet<>(Arrays.asList("alice", "bob", "charlie"));
        String user = "bob";
        if (validUsers.contains(user)) {
            System.out.println("\n" + user + " is a valid user (O(1) lookup)");
        }

        // Use Case 4: Finding common elements
        HashSet<String> team1 = new HashSet<>(Arrays.asList("Alice", "Bob", "Charlie"));
        HashSet<String> team2 = new HashSet<>(Arrays.asList("Bob", "David", "Charlie"));
        HashSet<String> common = new HashSet<>(team1);
        common.retainAll(team2);
        System.out.println("\nCommon members in both teams: " + common);

        // Use Case 5: Unique character count
        String text = "hello world";
        HashSet<Character> uniqueChars = new HashSet<>();
        for (char c : text.toCharArray()) {
            if (c != ' ')
                uniqueChars.add(c);
        }
        System.out.println("\nUnique characters in '" + text + "': " + uniqueChars.size());
        System.out.println("Characters: " + uniqueChars);

        System.out.println("\n=== End of HashSet Example ===");
    }
}
