package com.ashokmurugan.collections.map;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.Collection;

/**
 * HashMap Example - Hash Table Based Map Implementation
 * 
 * EXPLANATION:
 * HashMap is a hash table based implementation of the Map interface.
 * It stores key-value pairs and uses hashing to provide fast access.
 * Does not maintain any order of keys.
 * 
 * KEY CHARACTERISTICS:
 * - Implements Map, Cloneable, Serializable
 * - Stores key-value pairs
 * - No duplicate keys allowed (values can be duplicate)
 * - No guaranteed order
 * - Allows one null key and multiple null values
 * - Not synchronized (not thread-safe)
 * - Best performance for basic operations
 * 
 * INTERNAL STRUCTURE:
 * - Uses array of Node<K,V>[] (buckets)
 * - Each bucket can contain a linked list or tree (if too many collisions)
 * - Default initial capacity: 16
 * - Default load factor: 0.75
 * - Resizes when: size > capacity * loadFactor
 * - Since Java 8: Converts bucket to TreeNode when > 8 elements
 * (TREEIFY_THRESHOLD)
 * 
 * Node Structure:
 * class Node<K,V> {
 * final int hash;
 * final K key;
 * V value;
 * Node<K,V> next;
 * }
 * 
 * HASH FUNCTION:
 * - Uses hashCode() of key
 * - Applies additional hash function to reduce collisions
 * - Index = hash & (capacity - 1)
 * 
 * TIME COMPLEXITY (assuming good hash function):
 * - put(K key, V value) : O(1) average, O(n) worst case
 * - get(Object key) : O(1) average, O(n) worst case
 * - remove(Object key) : O(1) average, O(n) worst case
 * - containsKey(Object) : O(1) average, O(n) worst case
 * - containsValue(Object) : O(n) - needs to scan all entries
 * - size() : O(1)
 * - isEmpty() : O(1)
 * - clear() : O(n)
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of entries
 * 
 * WHEN TO USE:
 * ✓ Need fast key-value lookups
 * ✓ Order doesn't matter
 * ✓ Implementing caches, dictionaries, indexes
 * ✓ Counting occurrences
 * ✗ Need to maintain insertion order (use LinkedHashMap)
 * ✗ Need sorted keys (use TreeMap)
 * ✗ Thread-safe operations (use ConcurrentHashMap)
 */
public class HashMapExample {

    public static void main(String[] args) {
        System.out.println("=== HashMap Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Basic Operations
        demonstrateBasicOperations();

        // 3. Advanced Operations (Java 8+)
        demonstrateAdvancedOperations();

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
        HashMap<String, Integer> map1 = new HashMap<>();
        System.out.println("Empty HashMap: " + map1);

        // Constructor with initial capacity
        HashMap<String, String> map2 = new HashMap<>(32);
        System.out.println("HashMap with capacity 32: " + map2);

        // Constructor with capacity and load factor
        HashMap<Integer, String> map3 = new HashMap<>(32, 0.8f);
        System.out.println("HashMap with capacity 32, load factor 0.8: " + map3);

        // Constructor with map
        Map<String, Integer> sourceMap = Map.of("A", 1, "B", 2, "C", 3);
        HashMap<String, Integer> map4 = new HashMap<>(sourceMap);
        System.out.println("HashMap from map: " + map4);

        // Using Map.of() for immutable maps (Java 9+)
        Map<String, Integer> immutable = Map.of("X", 10, "Y", 20, "Z", 30);
        System.out.println("Immutable map: " + immutable);

        // Using Map.ofEntries() for more than 10 entries
        Map<String, Integer> largeMap = Map.ofEntries(
                Map.entry("K1", 1),
                Map.entry("K2", 2),
                Map.entry("K3", 3));
        System.out.println("Map from entries: " + largeMap);

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");

        HashMap<String, Integer> ages = new HashMap<>();

        // put - O(1) average
        ages.put("Alice", 30);
        ages.put("Bob", 25);
        ages.put("Charlie", 35);
        System.out.println("After put: " + ages);

        // put with duplicate key - replaces value
        Integer oldValue = ages.put("Alice", 31);
        System.out.println("Old value for Alice: " + oldValue);
        System.out.println("After update: " + ages);

        // get - O(1) average
        Integer age = ages.get("Bob");
        System.out.println("Bob's age: " + age);

        // get non-existent key - returns null
        Integer missing = ages.get("David");
        System.out.println("David's age: " + missing);

        // getOrDefault - O(1) average
        Integer defaultAge = ages.getOrDefault("David", 0);
        System.out.println("David's age (with default): " + defaultAge);

        // containsKey - O(1) average
        boolean hasAlice = ages.containsKey("Alice");
        System.out.println("Contains Alice: " + hasAlice);

        // containsValue - O(n) - scans all values
        boolean has25 = ages.containsValue(25);
        System.out.println("Contains value 25: " + has25);

        // remove - O(1) average
        Integer removed = ages.remove("Bob");
        System.out.println("Removed Bob: " + removed);
        System.out.println("After removal: " + ages);

        // size - O(1)
        System.out.println("Size: " + ages.size());

        // isEmpty - O(1)
        System.out.println("Is empty: " + ages.isEmpty());

        // clear - O(n)
        HashMap<String, Integer> temp = new HashMap<>(ages);
        temp.clear();
        System.out.println("After clear: " + temp);

        System.out.println();
    }

    private static void demonstrateAdvancedOperations() {
        System.out.println("3. ADVANCED OPERATIONS (Java 8+)");
        System.out.println("---------------------------------");

        HashMap<String, Integer> scores = new HashMap<>();
        scores.put("Alice", 85);
        scores.put("Bob", 90);
        scores.put("Charlie", 78);

        System.out.println("Original: " + scores);
        System.out.println();

        // putIfAbsent - only puts if key doesn't exist
        scores.putIfAbsent("Alice", 100); // Won't update
        scores.putIfAbsent("David", 95); // Will add
        System.out.println("After putIfAbsent: " + scores);

        // compute - computes new value for key
        scores.compute("Alice", (key, value) -> value + 5);
        System.out.println("After compute (Alice +5): " + scores);

        // computeIfPresent - computes only if key exists
        scores.computeIfPresent("Bob", (key, value) -> value + 10);
        scores.computeIfPresent("Eve", (key, value) -> 100); // Won't add
        System.out.println("After computeIfPresent: " + scores);

        // computeIfAbsent - computes only if key doesn't exist
        scores.computeIfAbsent("Eve", key -> 88);
        scores.computeIfAbsent("Alice", key -> 100); // Won't update
        System.out.println("After computeIfAbsent: " + scores);

        // merge - merges value with existing value
        scores.merge("Alice", 10, (oldVal, newVal) -> oldVal + newVal);
        scores.merge("Frank", 92, (oldVal, newVal) -> oldVal + newVal); // Just adds
        System.out.println("After merge: " + scores);

        // replace - replaces value for key
        scores.replace("Bob", 100);
        System.out.println("After replace Bob: " + scores);

        // replace with old value check
        boolean replaced = scores.replace("Charlie", 78, 80);
        System.out.println("Replaced Charlie (78->80): " + replaced);
        System.out.println("After conditional replace: " + scores);

        // remove with value check
        boolean removed = scores.remove("Frank", 92);
        System.out.println("Removed Frank with value 92: " + removed);
        System.out.println("Final: " + scores);

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("4. ITERATION METHODS");
        System.out.println("--------------------");

        HashMap<String, String> capitals = new HashMap<>();
        capitals.put("USA", "Washington DC");
        capitals.put("UK", "London");
        capitals.put("France", "Paris");
        capitals.put("Japan", "Tokyo");

        System.out.println("Note: HashMap does NOT maintain order!");
        System.out.println();

        // 1. Iterate over keys
        System.out.println("Keys:");
        Set<String> keys = capitals.keySet();
        for (String key : keys) {
            System.out.println("  " + key);
        }

        // 2. Iterate over values
        System.out.println("\nValues:");
        Collection<String> values = capitals.values();
        for (String value : values) {
            System.out.println("  " + value);
        }

        // 3. Iterate over entries (most common)
        System.out.println("\nEntries (for loop):");
        Set<Map.Entry<String, String>> entries = capitals.entrySet();
        for (Map.Entry<String, String> entry : entries) {
            System.out.println("  " + entry.getKey() + " -> " + entry.getValue());
        }

        // 4. forEach with lambda (Java 8+)
        System.out.println("\nEntries (forEach):");
        capitals.forEach((key, value) -> System.out.println("  " + key + " -> " + value));

        // 5. Stream API
        System.out.println("\nFiltered entries (Stream):");
        capitals.entrySet().stream()
                .filter(entry -> entry.getValue().length() > 5)
                .forEach(entry -> System.out.println("  " + entry.getKey() + " -> " + entry.getValue()));

        // 6. replaceAll - transform all values
        HashMap<String, Integer> numbers = new HashMap<>();
        numbers.put("one", 1);
        numbers.put("two", 2);
        numbers.put("three", 3);
        System.out.println("\nBefore replaceAll: " + numbers);
        numbers.replaceAll((key, value) -> value * 10);
        System.out.println("After replaceAll (*10): " + numbers);

        System.out.println();
    }

    private static void demonstrateNullHandling() {
        System.out.println("5. NULL HANDLING");
        System.out.println("----------------");

        HashMap<String, String> map = new HashMap<>();

        // HashMap allows one null key
        map.put(null, "NullKey");
        map.put("A", "ValueA");
        map.put("B", null); // Null value is allowed
        map.put("C", null); // Multiple null values allowed

        System.out.println("Map with nulls: " + map);

        // Get null key
        String nullKeyValue = map.get(null);
        System.out.println("Value for null key: " + nullKeyValue);

        // Contains null key
        boolean hasNullKey = map.containsKey(null);
        System.out.println("Contains null key: " + hasNullKey);

        // Contains null value
        boolean hasNullValue = map.containsValue(null);
        System.out.println("Contains null value: " + hasNullValue);

        // Update null key
        map.put(null, "UpdatedNullKey");
        System.out.println("After updating null key: " + map);

        // Remove null key
        map.remove(null);
        System.out.println("After removing null key: " + map);

        System.out.println();
    }

    private static void demonstrateHashCodeEquals() {
        System.out.println("6. HASHCODE AND EQUALS");
        System.out.println("----------------------");

        // Custom key class
        class Person {
            String name;
            int id;

            Person(String name, int id) {
                this.name = name;
                this.id = id;
            }

            @Override
            public boolean equals(Object o) {
                if (this == o)
                    return true;
                if (o == null || getClass() != o.getClass())
                    return false;
                Person person = (Person) o;
                return id == person.id && name.equals(person.name);
            }

            @Override
            public int hashCode() {
                return java.util.Objects.hash(name, id);
            }

            @Override
            public String toString() {
                return name + "(" + id + ")";
            }
        }

        HashMap<Person, String> personMap = new HashMap<>();
        Person p1 = new Person("Alice", 1);
        Person p2 = new Person("Bob", 2);

        personMap.put(p1, "Engineer");
        personMap.put(p2, "Manager");

        System.out.println("Person map: " + personMap);

        // Lookup with new object (same values)
        Person p3 = new Person("Alice", 1);
        String role = personMap.get(p3);
        System.out.println("Role for new Person('Alice', 1): " + role);
        System.out.println("(Works because of proper hashCode/equals)");

        System.out.println("\nImportant: Keys must have proper hashCode() and equals()!");
        System.out.println("Contract:");
        System.out.println("1. If a.equals(b), then a.hashCode() == b.hashCode()");
        System.out.println("2. If a.hashCode() == b.hashCode(), a may or may not equal b");
        System.out.println("3. hashCode() should be consistent (same value for same object)");
        System.out.println("4. Mutable keys are dangerous - don't modify after insertion!");

        System.out.println();
    }

    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        HashMap<Integer, String> map = new HashMap<>();

        // Put operations - O(1) average
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            map.put(i, "Value" + i);
        }
        long end = System.nanoTime();
        System.out.println("Put 100,000 entries: " + (end - start) / 1000000 + " ms");

        // Get operations - O(1) average
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            String value = map.get(i);
        }
        end = System.nanoTime();
        System.out.println("Get 100,000 entries: " + (end - start) / 1000000 + " ms");

        // ContainsKey - O(1) average
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            boolean contains = map.containsKey(i);
        }
        end = System.nanoTime();
        System.out.println("ContainsKey 100,000 times: " + (end - start) / 1000000 + " ms");

        // ContainsValue - O(n) - slow!
        start = System.nanoTime();
        boolean contains = map.containsValue("Value50000");
        end = System.nanoTime();
        System.out.println("ContainsValue once: " + (end - start) / 1000 + " μs (SLOW - O(n))");

        // Remove operations - O(1) average
        start = System.nanoTime();
        for (int i = 0; i < 50000; i++) {
            map.remove(i);
        }
        end = System.nanoTime();
        System.out.println("Remove 50,000 entries: " + (end - start) / 1000000 + " ms");

        System.out.println("\nHashMap provides constant-time performance for basic operations");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("8. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Counting occurrences (frequency map)
        String text = "hello world hello java world";
        HashMap<String, Integer> wordCount = new HashMap<>();
        for (String word : text.split(" ")) {
            wordCount.put(word, wordCount.getOrDefault(word, 0) + 1);
        }
        System.out.println("Word frequency: " + wordCount);

        // Use Case 2: Grouping data
        String[] names = { "Alice", "Bob", "Charlie", "Anna", "David", "Alex" };
        HashMap<Character, java.util.List<String>> groupedByFirstLetter = new HashMap<>();
        for (String name : names) {
            char firstLetter = name.charAt(0);
            groupedByFirstLetter.computeIfAbsent(firstLetter, k -> new java.util.ArrayList<>())
                    .add(name);
        }
        System.out.println("\nGrouped by first letter: " + groupedByFirstLetter);

        // Use Case 3: Caching/Memoization
        HashMap<Integer, Integer> fibCache = new HashMap<>();
        System.out.println("\nFibonacci with caching:");
        System.out.println("fib(10) = " + fibonacci(10, fibCache));
        System.out.println("fib(20) = " + fibonacci(20, fibCache));
        System.out.println("Cache size: " + fibCache.size());

        // Use Case 4: Index/Lookup table
        HashMap<String, String> phoneBook = new HashMap<>();
        phoneBook.put("Alice", "123-456-7890");
        phoneBook.put("Bob", "234-567-8901");
        phoneBook.put("Charlie", "345-678-9012");
        System.out.println("\nPhone book lookup:");
        System.out.println("Alice's phone: " + phoneBook.get("Alice"));

        // Use Case 5: Two-sum problem
        int[] nums = { 2, 7, 11, 15 };
        int target = 9;
        HashMap<Integer, Integer> numMap = new HashMap<>();
        System.out.println("\nTwo-sum problem (target=" + target + "):");
        for (int i = 0; i < nums.length; i++) {
            int complement = target - nums[i];
            if (numMap.containsKey(complement)) {
                System.out.println("Indices: [" + numMap.get(complement) + ", " + i + "]");
                System.out.println("Values: [" + complement + ", " + nums[i] + "]");
                break;
            }
            numMap.put(nums[i], i);
        }

        System.out.println("\n=== End of HashMap Example ===");
    }

    private static int fibonacci(int n, HashMap<Integer, Integer> cache) {
        if (n <= 1)
            return n;
        if (cache.containsKey(n))
            return cache.get(n);

        int result = fibonacci(n - 1, cache) + fibonacci(n - 2, cache);
        cache.put(n, result);
        return result;
    }
}
