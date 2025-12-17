package com.ashokmurugan.collections.map;

import java.util.TreeMap;
import java.util.Map;
import java.util.Comparator;
import java.util.NavigableMap;

/**
 * TreeMap Example - Red-Black Tree Based Sorted Map Implementation
 * 
 * EXPLANATION:
 * TreeMap is a NavigableMap implementation based on a Red-Black Tree.
 * Keys are stored in sorted order (natural ordering or custom Comparator).
 * Provides guaranteed log(n) time cost for basic operations.
 * 
 * KEY CHARACTERISTICS:
 * - Implements NavigableMap, SortedMap, Map, Cloneable, Serializable
 * - Keys stored in sorted order
 * - No duplicate keys allowed (values can be duplicate)
 * - Does NOT allow null keys (throws NullPointerException)
 * - Allows null values
 * - Not synchronized (not thread-safe)
 * - Slower than HashMap but maintains order
 * 
 * INTERNAL STRUCTURE:
 * - Uses Red-Black Tree (self-balancing BST)
 * - Each node contains: key, value, left, right, parent, color
 * - Height is always O(log n)
 * 
 * RED-BLACK TREE PROPERTIES:
 * 1. Every node is either red or black
 * 2. Root is always black
 * 3. All leaves (null) are black
 * 4. Red nodes cannot have red children
 * 5. All paths from root to leaves have same number of black nodes
 * 
 * TIME COMPLEXITY:
 * - put(K key, V value) : O(log n)
 * - get(Object key) : O(log n)
 * - remove(Object key) : O(log n)
 * - containsKey(Object) : O(log n)
 * - containsValue(Object) : O(n) - needs to scan all values
 * - firstKey() : O(log n)
 * - lastKey() : O(log n)
 * - higherKey(K key) : O(log n)
 * - lowerKey(K key) : O(log n)
 * - ceilingKey(K key) : O(log n)
 * - floorKey(K key) : O(log n)
 * - size() : O(1)
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of entries
 * 
 * WHEN TO USE:
 * ✓ Need keys in sorted order
 * ✓ Need to find min/max keys quickly
 * ✓ Need range queries (subMap, headMap, tailMap)
 * ✓ Need navigation operations (higher, lower, ceiling, floor)
 * ✓ Implementing time-based data structures
 * ✗ Need fastest possible operations (use HashMap)
 * ✗ Order doesn't matter (use HashMap)
 * ✗ Need to maintain insertion order (use LinkedHashMap)
 */
public class TreeMapExample {

    public static void main(String[] args) {
        System.out.println("=== TreeMap Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Basic Operations
        demonstrateBasicOperations();

        // 3. Navigation Operations
        demonstrateNavigationOperations();

        // 4. Range View Operations
        demonstrateRangeOperations();

        // 5. Custom Comparator
        demonstrateCustomComparator();

        // 6. Iteration Methods
        demonstrateIteration();

        // 7. Performance Characteristics
        demonstratePerformance();

        // 8. Practical Use Cases
        demonstratePracticalUseCases();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor - natural ordering
        TreeMap<Integer, String> map1 = new TreeMap<>();
        map1.put(3, "Three");
        map1.put(1, "One");
        map1.put(2, "Two");
        System.out.println("Natural ordering: " + map1);

        // Constructor with Comparator - reverse order
        TreeMap<Integer, String> map2 = new TreeMap<>(Comparator.reverseOrder());
        map2.put(3, "Three");
        map2.put(1, "One");
        map2.put(2, "Two");
        System.out.println("Reverse ordering: " + map2);

        // Constructor with map
        Map<String, Integer> sourceMap = Map.of("A", 1, "C", 3, "B", 2);
        TreeMap<String, Integer> map3 = new TreeMap<>(sourceMap);
        System.out.println("From map (sorted): " + map3);

        // Constructor with SortedMap
        TreeMap<String, Integer> map4 = new TreeMap<>(map3);
        System.out.println("From SortedMap: " + map4);

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");

        TreeMap<String, Integer> scores = new TreeMap<>();

        // put - O(log n) - automatically sorted by key
        scores.put("Charlie", 85);
        scores.put("Alice", 95);
        scores.put("Bob", 90);
        scores.put("David", 78);
        System.out.println("After put (auto-sorted): " + scores);

        // put with duplicate key - replaces value
        Integer oldValue = scores.put("Alice", 97);
        System.out.println("Old value for Alice: " + oldValue);
        System.out.println("After update: " + scores);

        // get - O(log n)
        Integer bobScore = scores.get("Bob");
        System.out.println("Bob's score: " + bobScore);

        // getOrDefault - O(log n)
        Integer eveScore = scores.getOrDefault("Eve", 0);
        System.out.println("Eve's score (default): " + eveScore);

        // containsKey - O(log n)
        boolean hasAlice = scores.containsKey("Alice");
        System.out.println("Contains Alice: " + hasAlice);

        // containsValue - O(n)
        boolean has90 = scores.containsValue(90);
        System.out.println("Contains value 90: " + has90);

        // firstKey and lastKey - O(log n)
        String first = scores.firstKey();
        String last = scores.lastKey();
        System.out.println("First key: " + first);
        System.out.println("Last key: " + last);

        // firstEntry and lastEntry - O(log n)
        Map.Entry<String, Integer> firstEntry = scores.firstEntry();
        Map.Entry<String, Integer> lastEntry = scores.lastEntry();
        System.out.println("First entry: " + firstEntry);
        System.out.println("Last entry: " + lastEntry);

        // pollFirstEntry and pollLastEntry - O(log n)
        Map.Entry<String, Integer> polledFirst = scores.pollFirstEntry();
        Map.Entry<String, Integer> polledLast = scores.pollLastEntry();
        System.out.println("Polled first: " + polledFirst + ", last: " + polledLast);
        System.out.println("After polling: " + scores);

        // remove - O(log n)
        Integer removed = scores.remove("Bob");
        System.out.println("Removed Bob: " + removed);
        System.out.println("After removal: " + scores);

        // size - O(1)
        System.out.println("Size: " + scores.size());

        System.out.println();
    }

    private static void demonstrateNavigationOperations() {
        System.out.println("3. NAVIGATION OPERATIONS");
        System.out.println("------------------------");

        TreeMap<Integer, String> map = new TreeMap<>();
        map.put(10, "Ten");
        map.put(20, "Twenty");
        map.put(30, "Thirty");
        map.put(40, "Forty");
        map.put(50, "Fifty");
        map.put(60, "Sixty");

        System.out.println("Map: " + map);
        System.out.println();

        // higherKey(k) - least key strictly greater than k - O(log n)
        Integer higher25 = map.higherKey(25);
        Integer higher40 = map.higherKey(40);
        System.out.println("higherKey(25): " + higher25 + " -> " + map.get(higher25));
        System.out.println("higherKey(40): " + higher40 + " -> " + map.get(higher40));

        // lowerKey(k) - greatest key strictly less than k - O(log n)
        Integer lower25 = map.lowerKey(25);
        Integer lower40 = map.lowerKey(40);
        System.out.println("lowerKey(25): " + lower25 + " -> " + map.get(lower25));
        System.out.println("lowerKey(40): " + lower40 + " -> " + map.get(lower40));

        // ceilingKey(k) - least key >= k - O(log n)
        Integer ceiling25 = map.ceilingKey(25);
        Integer ceiling40 = map.ceilingKey(40);
        System.out.println("ceilingKey(25): " + ceiling25 + " -> " + map.get(ceiling25));
        System.out.println("ceilingKey(40): " + ceiling40 + " -> " + map.get(ceiling40));

        // floorKey(k) - greatest key <= k - O(log n)
        Integer floor25 = map.floorKey(25);
        Integer floor40 = map.floorKey(40);
        System.out.println("floorKey(25): " + floor25 + " -> " + map.get(floor25));
        System.out.println("floorKey(40): " + floor40 + " -> " + map.get(floor40));

        // higherEntry, lowerEntry, ceilingEntry, floorEntry
        System.out.println("\nEntry methods:");
        Map.Entry<Integer, String> higherEntry = map.higherEntry(25);
        Map.Entry<Integer, String> lowerEntry = map.lowerEntry(25);
        System.out.println("higherEntry(25): " + higherEntry);
        System.out.println("lowerEntry(25): " + lowerEntry);

        // Edge cases
        System.out.println("\nEdge cases:");
        System.out.println("higherKey(60): " + map.higherKey(60) + " (null)");
        System.out.println("lowerKey(10): " + map.lowerKey(10) + " (null)");

        System.out.println();
    }

    private static void demonstrateRangeOperations() {
        System.out.println("4. RANGE VIEW OPERATIONS");
        System.out.println("------------------------");

        TreeMap<Integer, String> map = new TreeMap<>();
        for (int i = 10; i <= 90; i += 10) {
            map.put(i, "Value" + i);
        }

        System.out.println("Original map: " + map);
        System.out.println();

        // headMap(k) - keys < k
        NavigableMap<Integer, String> headMap = map.headMap(50, false);
        System.out.println("headMap(50, false): " + headMap + " (keys < 50)");

        // headMap(k, inclusive) - keys <= k
        NavigableMap<Integer, String> headMapInc = map.headMap(50, true);
        System.out.println("headMap(50, true): " + headMapInc + " (keys <= 50)");

        // tailMap(k) - keys >= k
        NavigableMap<Integer, String> tailMap = map.tailMap(50, true);
        System.out.println("tailMap(50, true): " + tailMap + " (keys >= 50)");

        // tailMap(k, inclusive) - keys > k
        NavigableMap<Integer, String> tailMapExc = map.tailMap(50, false);
        System.out.println("tailMap(50, false): " + tailMapExc + " (keys > 50)");

        // subMap(from, to) - keys >= from and < to
        NavigableMap<Integer, String> subMap = map.subMap(30, false, 70, false);
        System.out.println("subMap(30, false, 70, false): " + subMap + " (30 < keys < 70)");

        // subMap with inclusive flags
        NavigableMap<Integer, String> subMapInc = map.subMap(30, true, 70, true);
        System.out.println("subMap(30, true, 70, true): " + subMapInc + " (30 <= keys <= 70)");

        // descendingMap - reversed view
        NavigableMap<Integer, String> descMap = map.descendingMap();
        System.out.println("descendingMap: " + descMap);

        // These are VIEWS - changes reflect in original map
        System.out.println("\nViews are backed by original map:");
        headMap.put(25, "Value25");
        System.out.println("After headMap.put(25): " + map);

        System.out.println();
    }

    private static void demonstrateCustomComparator() {
        System.out.println("5. CUSTOM COMPARATOR");
        System.out.println("--------------------");

        // String length comparator
        TreeMap<String, Integer> byLength = new TreeMap<>(
                Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()));

        byLength.put("apple", 5);
        byLength.put("pie", 3);
        byLength.put("banana", 6);
        byLength.put("kiwi", 4);
        byLength.put("strawberry", 10);

        System.out.println("Sorted by key length: " + byLength);

        // Custom class with natural ordering
        class Person implements Comparable<Person> {
            String name;
            int age;

            Person(String name, int age) {
                this.name = name;
                this.age = age;
            }

            @Override
            public int compareTo(Person other) {
                return this.name.compareTo(other.name);
            }

            @Override
            public String toString() {
                return name + "(" + age + ")";
            }
        }

        TreeMap<Person, String> peopleMap = new TreeMap<>();
        peopleMap.put(new Person("Charlie", 35), "Engineer");
        peopleMap.put(new Person("Alice", 30), "Manager");
        peopleMap.put(new Person("Bob", 25), "Designer");

        System.out.println("People map (sorted by name): " + peopleMap);

        // Reverse order
        TreeMap<Integer, String> reverseMap = new TreeMap<>(Comparator.reverseOrder());
        reverseMap.put(1, "One");
        reverseMap.put(2, "Two");
        reverseMap.put(3, "Three");
        System.out.println("Reverse order: " + reverseMap);

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("6. ITERATION METHODS");
        System.out.println("--------------------");

        TreeMap<String, Integer> map = new TreeMap<>();
        map.put("Mango", 50);
        map.put("Apple", 30);
        map.put("Banana", 20);
        map.put("Cherry", 40);

        System.out.println("TreeMap (sorted by key): " + map);
        System.out.println();

        // 1. Iterate over keys (ascending)
        System.out.println("Keys (ascending):");
        for (String key : map.keySet()) {
            System.out.println("  " + key);
        }

        // 2. Iterate over keys (descending)
        System.out.println("\nKeys (descending):");
        for (String key : map.descendingKeySet()) {
            System.out.println("  " + key);
        }

        // 3. Iterate over values
        System.out.println("\nValues:");
        for (Integer value : map.values()) {
            System.out.println("  " + value);
        }

        // 4. Iterate over entries
        System.out.println("\nEntries (for loop):");
        for (Map.Entry<String, Integer> entry : map.entrySet()) {
            System.out.println("  " + entry.getKey() + " -> " + entry.getValue());
        }

        // 5. forEach with lambda
        System.out.println("\nEntries (forEach):");
        map.forEach((key, value) -> System.out.println("  " + key + " -> " + value));

        // 6. Stream API
        System.out.println("\nFiltered entries (value > 30):");
        map.entrySet().stream()
                .filter(entry -> entry.getValue() > 30)
                .forEach(entry -> System.out.println("  " + entry.getKey() + " -> " + entry.getValue()));

        System.out.println();
    }

    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        TreeMap<Integer, String> treeMap = new TreeMap<>();
        java.util.HashMap<Integer, String> hashMap = new java.util.HashMap<>();

        // Put operations
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            treeMap.put(i, "Value" + i);
        }
        long end = System.nanoTime();
        System.out.println("TreeMap - Put 100,000: " + (end - start) / 1000000 + " ms (O(log n))");

        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            hashMap.put(i, "Value" + i);
        }
        end = System.nanoTime();
        System.out.println("HashMap - Put 100,000: " + (end - start) / 1000000 + " ms (O(1))");

        // Get operations
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            String value = treeMap.get(i);
        }
        end = System.nanoTime();
        System.out.println("TreeMap - Get 100,000: " + (end - start) / 1000000 + " ms (O(log n))");

        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            String value = hashMap.get(i);
        }
        end = System.nanoTime();
        System.out.println("HashMap - Get 100,000: " + (end - start) / 1000000 + " ms (O(1))");

        System.out.println("\nTreeMap is slower but provides ordering and navigation");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("8. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Time-series data
        TreeMap<Long, Double> stockPrices = new TreeMap<>();
        stockPrices.put(1000L, 100.5);
        stockPrices.put(2000L, 102.3);
        stockPrices.put(3000L, 101.8);
        stockPrices.put(4000L, 105.2);
        stockPrices.put(5000L, 103.7);

        System.out.println("Stock prices (timestamp -> price):");
        stockPrices.forEach((time, price) -> System.out.println("  " + time + " -> $" + price));

        // Find price at specific time or closest before
        long queryTime = 3500L;
        Long closestTime = stockPrices.floorKey(queryTime);
        System.out.println("\nPrice at or before " + queryTime + ": $" + stockPrices.get(closestTime));

        // Range query - prices between timestamps
        NavigableMap<Long, Double> range = stockPrices.subMap(2000L, true, 4000L, true);
        System.out.println("Prices between 2000-4000: " + range);

        // Use Case 2: Leaderboard with scores
        TreeMap<Integer, String> leaderboard = new TreeMap<>(Comparator.reverseOrder());
        leaderboard.put(1500, "Alice");
        leaderboard.put(1200, "Bob");
        leaderboard.put(1800, "Charlie");
        leaderboard.put(1350, "David");

        System.out.println("\nLeaderboard (score -> player):");
        int rank = 1;
        for (Map.Entry<Integer, String> entry : leaderboard.entrySet()) {
            System.out.println("  " + rank++ + ". " + entry.getValue() + " - " + entry.getKey());
        }

        // Use Case 3: Dictionary with range lookup
        TreeMap<String, String> dictionary = new TreeMap<>();
        dictionary.put("apple", "A fruit");
        dictionary.put("application", "A software program");
        dictionary.put("apply", "To put into action");
        dictionary.put("banana", "A yellow fruit");
        dictionary.put("band", "A musical group");

        System.out.println("\nWords starting with 'app':");
        String prefix = "app";
        NavigableMap<String, String> words = dictionary.subMap(
                prefix, true,
                prefix + Character.MAX_VALUE, true);
        words.forEach((word, def) -> System.out.println("  " + word + ": " + def));

        // Use Case 4: Event scheduling
        class Event {
            String name;
            String description;

            Event(String name, String description) {
                this.name = name;
                this.description = description;
            }

            @Override
            public String toString() {
                return name + " - " + description;
            }
        }

        TreeMap<Integer, Event> schedule = new TreeMap<>();
        schedule.put(900, new Event("Meeting", "Team standup"));
        schedule.put(1000, new Event("Code Review", "PR #123"));
        schedule.put(1400, new Event("Lunch", "Break"));
        schedule.put(1500, new Event("Development", "Feature work"));

        System.out.println("\nToday's schedule:");
        schedule.forEach((time, event) -> {
            int hour = time / 100;
            int minute = time % 100;
            System.out.printf("  %02d:%02d - %s%n", hour, minute, event);
        });

        // Find next event after current time
        int currentTime = 1030;
        Map.Entry<Integer, Event> nextEvent = schedule.ceilingEntry(currentTime);
        if (nextEvent != null) {
            System.out.println("\nNext event after " + currentTime + ": " + nextEvent.getValue());
        }

        System.out.println("\n=== End of TreeMap Example ===");
    }
}
