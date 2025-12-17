package com.ashokmurugan.collections.set;

import java.util.TreeSet;
import java.util.Comparator;
import java.util.Iterator;
import java.util.Arrays;

/**
 * TreeSet Example - Red-Black Tree Based Sorted Set Implementation
 * 
 * EXPLANATION:
 * TreeSet is a NavigableSet implementation based on a TreeMap (Red-Black Tree).
 * Elements are stored in sorted order (natural ordering or custom Comparator).
 * Provides guaranteed log(n) time cost for basic operations.
 * 
 * KEY CHARACTERISTICS:
 * - Implements NavigableSet, SortedSet, Set, Cloneable, Serializable
 * - Elements stored in sorted order
 * - No duplicate elements allowed
 * - Does NOT allow null elements (throws NullPointerException)
 * - Not synchronized (not thread-safe)
 * - Slower than HashSet but maintains order
 * 
 * INTERNAL STRUCTURE:
 * - Uses TreeMap<E, Object> internally
 * - TreeMap uses Red-Black Tree (self-balancing BST)
 * - Elements are stored as keys in the TreeMap
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
 * - add(E e) : O(log n)
 * - remove(Object o) : O(log n)
 * - contains(Object o) : O(log n)
 * - first() : O(log n)
 * - last() : O(log n)
 * - pollFirst() : O(log n)
 * - pollLast() : O(log n)
 * - higher(E e) : O(log n)
 * - lower(E e) : O(log n)
 * - ceiling(E e) : O(log n)
 * - floor(E e) : O(log n)
 * - size() : O(1)
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of elements
 * 
 * WHEN TO USE:
 * ✓ Need elements in sorted order
 * ✓ Need to find min/max quickly
 * ✓ Need range queries (subSet, headSet, tailSet)
 * ✓ Need navigation operations (higher, lower, ceiling, floor)
 * ✓ Implementing priority-based systems
 * ✗ Need fastest possible operations (use HashSet)
 * ✗ Order doesn't matter (use HashSet)
 * ✗ Need to store null elements (use LinkedHashSet)
 */
public class TreeSetExample {

    public static void main(String[] args) {
        System.out.println("=== TreeSet Comprehensive Example ===\n");

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
        TreeSet<Integer> set1 = new TreeSet<>();
        set1.addAll(Arrays.asList(5, 2, 8, 1, 9));
        System.out.println("Natural ordering: " + set1);

        // Constructor with Comparator - reverse order
        TreeSet<Integer> set2 = new TreeSet<>(Comparator.reverseOrder());
        set2.addAll(Arrays.asList(5, 2, 8, 1, 9));
        System.out.println("Reverse ordering: " + set2);

        // Constructor with collection
        TreeSet<String> set3 = new TreeSet<>(Arrays.asList("Dog", "Cat", "Elephant", "Ant"));
        System.out.println("From collection: " + set3);

        // Constructor with SortedSet
        TreeSet<String> set4 = new TreeSet<>(set3);
        System.out.println("From SortedSet: " + set4);

        System.out.println();
    }

    private static void demonstrateBasicOperations() {
        System.out.println("2. BASIC OPERATIONS");
        System.out.println("-------------------");

        TreeSet<Integer> numbers = new TreeSet<>();

        // Adding elements - O(log n) - automatically sorted
        numbers.add(50);
        numbers.add(20);
        numbers.add(80);
        numbers.add(10);
        numbers.add(40);
        System.out.println("After adding (auto-sorted): " + numbers);

        // Adding duplicate - returns false
        boolean added = numbers.add(20);
        System.out.println("Added duplicate 20: " + added);
        System.out.println("Set: " + numbers + " (no change)");

        // Contains - O(log n)
        boolean has40 = numbers.contains(40);
        System.out.println("Contains 40: " + has40);

        // First and Last - O(log n)
        int first = numbers.first();
        int last = numbers.last();
        System.out.println("First element: " + first);
        System.out.println("Last element: " + last);

        // pollFirst and pollLast - O(log n) - retrieves and removes
        int polledFirst = numbers.pollFirst();
        int polledLast = numbers.pollLast();
        System.out.println("Polled first: " + polledFirst + ", last: " + polledLast);
        System.out.println("After polling: " + numbers);

        // Remove - O(log n)
        boolean removed = numbers.remove(40);
        System.out.println("Removed 40: " + removed);
        System.out.println("After removal: " + numbers);

        // Size - O(1)
        System.out.println("Size: " + numbers.size());

        System.out.println();
    }

    private static void demonstrateNavigationOperations() {
        System.out.println("3. NAVIGATION OPERATIONS");
        System.out.println("------------------------");

        TreeSet<Integer> numbers = new TreeSet<>(Arrays.asList(10, 20, 30, 40, 50, 60, 70));
        System.out.println("Set: " + numbers);
        System.out.println();

        // higher(e) - least element strictly greater than e - O(log n)
        Integer higher35 = numbers.higher(35);
        Integer higher50 = numbers.higher(50);
        System.out.println("higher(35): " + higher35 + " (next greater element)");
        System.out.println("higher(50): " + higher50);

        // lower(e) - greatest element strictly less than e - O(log n)
        Integer lower35 = numbers.lower(35);
        Integer lower50 = numbers.lower(50);
        System.out.println("lower(35): " + lower35 + " (previous smaller element)");
        System.out.println("lower(50): " + lower50);

        // ceiling(e) - least element >= e - O(log n)
        Integer ceiling35 = numbers.ceiling(35);
        Integer ceiling50 = numbers.ceiling(50);
        System.out.println("ceiling(35): " + ceiling35 + " (>= 35)");
        System.out.println("ceiling(50): " + ceiling50 + " (>= 50)");

        // floor(e) - greatest element <= e - O(log n)
        Integer floor35 = numbers.floor(35);
        Integer floor50 = numbers.floor(50);
        System.out.println("floor(35): " + floor35 + " (<= 35)");
        System.out.println("floor(50): " + floor50 + " (<= 50)");

        // Edge cases
        System.out.println("\nEdge cases:");
        System.out.println("higher(70): " + numbers.higher(70) + " (null - no element)");
        System.out.println("lower(10): " + numbers.lower(10) + " (null - no element)");

        System.out.println();
    }

    private static void demonstrateRangeOperations() {
        System.out.println("4. RANGE VIEW OPERATIONS");
        System.out.println("------------------------");

        TreeSet<Integer> numbers = new TreeSet<>(Arrays.asList(10, 20, 30, 40, 50, 60, 70, 80, 90));
        System.out.println("Original set: " + numbers);
        System.out.println();

        // headSet(e) - elements < e
        var headSet = numbers.headSet(50);
        System.out.println("headSet(50): " + headSet + " (elements < 50)");

        // headSet(e, inclusive) - elements <= e
        var headSetInclusive = numbers.headSet(50, true);
        System.out.println("headSet(50, true): " + headSetInclusive + " (elements <= 50)");

        // tailSet(e) - elements >= e
        var tailSet = numbers.tailSet(50);
        System.out.println("tailSet(50): " + tailSet + " (elements >= 50)");

        // tailSet(e, inclusive) - elements > e
        var tailSetExclusive = numbers.tailSet(50, false);
        System.out.println("tailSet(50, false): " + tailSetExclusive + " (elements > 50)");

        // subSet(from, to) - elements >= from and < to
        var subSet = numbers.subSet(30, 70);
        System.out.println("subSet(30, 70): " + subSet + " (30 <= x < 70)");

        // subSet with inclusive flags
        var subSetInclusive = numbers.subSet(30, true, 70, true);
        System.out.println("subSet(30, true, 70, true): " + subSetInclusive + " (30 <= x <= 70)");

        // These are VIEWS - changes reflect in original set
        System.out.println("\nViews are backed by original set:");
        headSet.remove(10);
        System.out.println("After headSet.remove(10): " + numbers);

        System.out.println();
    }

    private static void demonstrateCustomComparator() {
        System.out.println("5. CUSTOM COMPARATOR");
        System.out.println("--------------------");

        // String length comparator
        TreeSet<String> byLength = new TreeSet<>(Comparator.comparingInt(String::length)
                .thenComparing(Comparator.naturalOrder()));
        byLength.addAll(Arrays.asList("apple", "pie", "banana", "kiwi", "strawberry"));
        System.out.println("Sorted by length: " + byLength);

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
                return Integer.compare(this.age, other.age);
            }

            @Override
            public String toString() {
                return name + "(" + age + ")";
            }
        }

        TreeSet<Person> peopleByAge = new TreeSet<>();
        peopleByAge.add(new Person("Alice", 30));
        peopleByAge.add(new Person("Bob", 25));
        peopleByAge.add(new Person("Charlie", 35));
        peopleByAge.add(new Person("David", 25)); // Same age as Bob
        System.out.println("People sorted by age: " + peopleByAge);

        // Custom comparator for Person - by name
        TreeSet<Person> peopleByName = new TreeSet<>(Comparator.comparing(p -> p.name));
        peopleByName.add(new Person("Alice", 30));
        peopleByName.add(new Person("Bob", 25));
        peopleByName.add(new Person("Charlie", 35));
        System.out.println("People sorted by name: " + peopleByName);

        // Reverse order
        TreeSet<Integer> reverseNumbers = new TreeSet<>(Comparator.reverseOrder());
        reverseNumbers.addAll(Arrays.asList(5, 2, 8, 1, 9));
        System.out.println("Reverse order: " + reverseNumbers);

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("6. ITERATION METHODS");
        System.out.println("--------------------");

        TreeSet<String> fruits = new TreeSet<>(Arrays.asList("Mango", "Apple", "Banana", "Cherry"));
        System.out.println("TreeSet (sorted): " + fruits);
        System.out.println();

        // 1. Ascending order (default)
        System.out.print("Ascending: ");
        for (String fruit : fruits) {
            System.out.print(fruit + " ");
        }
        System.out.println();

        // 2. Descending order
        System.out.print("Descending: ");
        for (String fruit : fruits.descendingSet()) {
            System.out.print(fruit + " ");
        }
        System.out.println();

        // 3. Iterator
        System.out.print("Iterator: ");
        Iterator<String> iterator = fruits.iterator();
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();

        // 4. Descending Iterator
        System.out.print("Descending Iterator: ");
        Iterator<String> descIterator = fruits.descendingIterator();
        while (descIterator.hasNext()) {
            System.out.print(descIterator.next() + " ");
        }
        System.out.println();

        // 5. forEach with lambda
        System.out.print("forEach: ");
        fruits.forEach(f -> System.out.print(f + " "));
        System.out.println();

        // 6. Stream API
        System.out.print("Stream (filtered): ");
        fruits.stream()
                .filter(f -> f.length() > 5)
                .forEach(f -> System.out.print(f + " "));
        System.out.println("\n");
    }

    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        TreeSet<Integer> treeSet = new TreeSet<>();
        java.util.HashSet<Integer> hashSet = new java.util.HashSet<>();

        // Adding elements
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            treeSet.add(i);
        }
        long end = System.nanoTime();
        System.out.println("TreeSet - Add 100,000: " + (end - start) / 1000000 + " ms (O(log n))");

        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            hashSet.add(i);
        }
        end = System.nanoTime();
        System.out.println("HashSet - Add 100,000: " + (end - start) / 1000000 + " ms (O(1))");

        // Contains check
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            boolean contains = treeSet.contains(i);
        }
        end = System.nanoTime();
        System.out.println("TreeSet - Contains 100,000: " + (end - start) / 1000000 + " ms (O(log n))");

        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            boolean contains = hashSet.contains(i);
        }
        end = System.nanoTime();
        System.out.println("HashSet - Contains 100,000: " + (end - start) / 1000000 + " ms (O(1))");

        System.out.println("\nTreeSet is slower but provides ordering and navigation");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("8. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Maintaining sorted unique elements
        TreeSet<Integer> scores = new TreeSet<>();
        scores.addAll(Arrays.asList(85, 92, 78, 92, 95, 88, 78));
        System.out.println("Unique scores (sorted): " + scores);
        System.out.println("Highest score: " + scores.last());
        System.out.println("Lowest score: " + scores.first());

        // Use Case 2: Range queries
        TreeSet<Integer> ages = new TreeSet<>(Arrays.asList(18, 21, 25, 30, 35, 40, 45, 50, 55, 60));
        System.out.println("\nAll ages: " + ages);
        System.out.println("Young adults (18-30): " + ages.subSet(18, true, 30, true));
        System.out.println("Middle aged (30-50): " + ages.subSet(30, true, 50, true));
        System.out.println("Seniors (>= 55): " + ages.tailSet(55));

        // Use Case 3: Finding next/previous element
        TreeSet<Integer> timestamps = new TreeSet<>(Arrays.asList(100, 200, 300, 400, 500));
        int query = 250;
        System.out.println("\nTimestamps: " + timestamps);
        System.out.println("Query time: " + query);
        System.out.println("Previous timestamp: " + timestamps.floor(query));
        System.out.println("Next timestamp: " + timestamps.ceiling(query));

        // Use Case 4: Leaderboard
        class Player implements Comparable<Player> {
            String name;
            int score;

            Player(String name, int score) {
                this.name = name;
                this.score = score;
            }

            @Override
            public int compareTo(Player other) {
                // Higher score first, then alphabetically
                int scoreCompare = Integer.compare(other.score, this.score);
                return scoreCompare != 0 ? scoreCompare : this.name.compareTo(other.name);
            }

            @Override
            public String toString() {
                return name + ":" + score;
            }
        }

        TreeSet<Player> leaderboard = new TreeSet<>();
        leaderboard.add(new Player("Alice", 1500));
        leaderboard.add(new Player("Bob", 1200));
        leaderboard.add(new Player("Charlie", 1800));
        leaderboard.add(new Player("David", 1500));

        System.out.println("\nLeaderboard (sorted by score desc, then name):");
        int rank = 1;
        for (Player player : leaderboard) {
            System.out.println(rank++ + ". " + player);
        }

        System.out.println("\n=== End of TreeSet Example ===");
    }
}
