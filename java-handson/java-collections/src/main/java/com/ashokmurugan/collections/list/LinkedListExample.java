package com.ashokmurugan.collections.list;

import java.util.LinkedList;
import java.util.Iterator;
import java.util.List;
import java.util.ListIterator;

/**
 * LinkedList Example - Doubly-Linked List Implementation
 * 
 * EXPLANATION:
 * LinkedList is a doubly-linked list implementation of List and Deque
 * interfaces.
 * Each element (node) contains data and references to both next and previous
 * nodes.
 * 
 * KEY CHARACTERISTICS:
 * - Implements List, Deque, Queue, Cloneable, Serializable
 * - Allows duplicate elements
 * - Maintains insertion order
 * - Not synchronized (not thread-safe)
 * - Allows null elements
 * - No random access (no RandomAccess marker interface)
 * 
 * INTERNAL STRUCTURE:
 * - Uses Node<E> class with three fields: item, next, prev
 * - Maintains references to first and last nodes
 * - Size is tracked separately
 * 
 * Node Structure:
 * class Node<E> {
 * E item;
 * Node<E> next;
 * Node<E> prev;
 * }
 * 
 * TIME COMPLEXITY:
 * - add(E e) : O(1) - adds at end
 * - add(int index, E) : O(n) - needs to traverse to index
 * - addFirst(E e) : O(1) - adds at beginning
 * - addLast(E e) : O(1) - adds at end
 * - get(int index) : O(n) - needs to traverse
 * - getFirst() : O(1) - direct access
 * - getLast() : O(1) - direct access
 * - remove(int index) : O(n) - needs to traverse
 * - removeFirst() : O(1) - direct access
 * - removeLast() : O(1) - direct access
 * - remove(Object o) : O(n) - needs to search
 * - contains(Object o) : O(n) - linear search
 * - size() : O(1) - maintains size variable
 * 
 * SPACE COMPLEXITY: O(n) - each element requires extra space for two pointers
 * 
 * WHEN TO USE:
 * ✓ Frequent insertions/deletions at beginning or end
 * ✓ Implementing Queue or Deque
 * ✓ Frequent insertions/deletions in the middle (if you have iterator/node
 * reference)
 * ✓ Memory is not a constraint (uses more memory than ArrayList)
 * ✗ Frequent random access by index
 * ✗ Memory-constrained environments
 * 
 * ARRAYLIST vs LINKEDLIST:
 * - ArrayList: Better for random access, less memory overhead
 * - LinkedList: Better for insertions/deletions, implements Queue/Deque
 */
public class LinkedListExample {

    public static void main(String[] args) {
        System.out.println("=== LinkedList Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. List Operations
        demonstrateListOperations();

        // 3. Deque Operations (Double-Ended Queue)
        demonstrateDequeOperations();

        // 4. Queue Operations
        demonstrateQueueOperations();

        // 5. Stack Operations
        demonstrateStackOperations();

        // 6. Iteration Methods
        demonstrateIteration();

        // 7. Performance Comparison
        demonstratePerformance();

        // 8. Advanced Operations
        demonstrateAdvancedOperations();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor
        LinkedList<String> list1 = new LinkedList<>();
        System.out.println("Empty LinkedList: " + list1);

        // Constructor with collection
        List<Integer> sourceList = List.of(1, 2, 3, 4, 5);
        LinkedList<Integer> list2 = new LinkedList<>(sourceList);
        System.out.println("LinkedList from collection: " + list2);

        // LinkedList can be used as List, Deque, or Queue
        List<String> asList = new LinkedList<>();
        java.util.Deque<String> asDeque = new LinkedList<>();
        java.util.Queue<String> asQueue = new LinkedList<>();
        System.out.println("LinkedList implements List, Deque, and Queue");

        System.out.println();
    }

    private static void demonstrateListOperations() {
        System.out.println("2. LIST OPERATIONS");
        System.out.println("------------------");

        LinkedList<String> languages = new LinkedList<>();

        // Adding elements - O(1) at ends, O(n) at index
        languages.add("Java");
        languages.add("Python");
        languages.add("JavaScript");
        System.out.println("After adding: " + languages);

        // Adding at specific index - O(n)
        languages.add(1, "C++");
        System.out.println("After add at index 1: " + languages);

        // Getting element - O(n) - needs traversal
        String lang = languages.get(2);
        System.out.println("Element at index 2: " + lang);

        // Setting element - O(n)
        languages.set(0, "Java 17");
        System.out.println("After set index 0: " + languages);

        // Removing by index - O(n)
        String removed = languages.remove(1);
        System.out.println("Removed: " + removed + ", List: " + languages);

        // Removing by object - O(n)
        boolean isRemoved = languages.remove("JavaScript");
        System.out.println("Removed JavaScript: " + isRemoved + ", List: " + languages);

        // Size - O(1)
        System.out.println("Size: " + languages.size());

        System.out.println();
    }

    private static void demonstrateDequeOperations() {
        System.out.println("3. DEQUE OPERATIONS (Double-Ended Queue)");
        System.out.println("----------------------------------------");

        LinkedList<Integer> deque = new LinkedList<>();

        // Adding at both ends - O(1)
        deque.addFirst(2);
        deque.addFirst(1);
        deque.addLast(3);
        deque.addLast(4);
        System.out.println("After addFirst/addLast: " + deque);

        // offerFirst/offerLast - similar to addFirst/addLast but returns boolean
        deque.offerFirst(0);
        deque.offerLast(5);
        System.out.println("After offerFirst/offerLast: " + deque);

        // Accessing elements at both ends - O(1)
        System.out.println("First element (getFirst): " + deque.getFirst());
        System.out.println("Last element (getLast): " + deque.getLast());
        System.out.println("First element (peekFirst): " + deque.peekFirst());
        System.out.println("Last element (peekLast): " + deque.peekLast());

        // Removing from both ends - O(1)
        int first = deque.removeFirst();
        int last = deque.removeLast();
        System.out.println("Removed first: " + first + ", last: " + last);
        System.out.println("After removal: " + deque);

        // pollFirst/pollLast - similar to removeFirst/removeLast but returns null if
        // empty
        Integer polledFirst = deque.pollFirst();
        Integer polledLast = deque.pollLast();
        System.out.println("Polled first: " + polledFirst + ", last: " + polledLast);
        System.out.println("After polling: " + deque);

        System.out.println();
    }

    private static void demonstrateQueueOperations() {
        System.out.println("4. QUEUE OPERATIONS (FIFO)");
        System.out.println("---------------------------");

        LinkedList<String> queue = new LinkedList<>();

        // Enqueue (add to rear) - O(1)
        queue.offer("First");
        queue.offer("Second");
        queue.offer("Third");
        queue.offer("Fourth");
        System.out.println("Queue after offers: " + queue);

        // Peek (view front without removing) - O(1)
        String front = queue.peek();
        System.out.println("Front element (peek): " + front);
        System.out.println("Queue after peek: " + queue);

        // Dequeue (remove from front) - O(1)
        String dequeued = queue.poll();
        System.out.println("Dequeued: " + dequeued);
        System.out.println("Queue after poll: " + queue);

        // element() - similar to peek() but throws exception if empty
        String element = queue.element();
        System.out.println("Front element (element): " + element);

        // remove() - similar to poll() but throws exception if empty
        String removed = queue.remove();
        System.out.println("Removed: " + removed);
        System.out.println("Final queue: " + queue);

        System.out.println();
    }

    private static void demonstrateStackOperations() {
        System.out.println("5. STACK OPERATIONS (LIFO)");
        System.out.println("---------------------------");

        LinkedList<String> stack = new LinkedList<>();

        // Push (add to top) - O(1)
        stack.push("Bottom");
        stack.push("Middle");
        stack.push("Top");
        System.out.println("Stack after pushes: " + stack);

        // Peek (view top without removing) - O(1)
        String top = stack.peek();
        System.out.println("Top element (peek): " + top);

        // Pop (remove from top) - O(1)
        String popped = stack.pop();
        System.out.println("Popped: " + popped);
        System.out.println("Stack after pop: " + stack);

        // Continue popping
        while (!stack.isEmpty()) {
            System.out.println("Popping: " + stack.pop());
        }
        System.out.println("Stack is now empty: " + stack.isEmpty());

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("6. ITERATION METHODS");
        System.out.println("--------------------");

        LinkedList<String> colors = new LinkedList<>(List.of("Red", "Green", "Blue", "Yellow"));

        // 1. Enhanced for loop
        System.out.print("Enhanced for: ");
        for (String color : colors) {
            System.out.print(color + " ");
        }
        System.out.println();

        // 2. Iterator - forward iteration
        System.out.print("Iterator (forward): ");
        Iterator<String> iterator = colors.iterator();
        while (iterator.hasNext()) {
            System.out.print(iterator.next() + " ");
        }
        System.out.println();

        // 3. Descending Iterator - backward iteration
        System.out.print("Descending Iterator: ");
        Iterator<String> descIterator = colors.descendingIterator();
        while (descIterator.hasNext()) {
            System.out.print(descIterator.next() + " ");
        }
        System.out.println();

        // 4. ListIterator - bidirectional iteration
        System.out.print("ListIterator (forward): ");
        ListIterator<String> listIterator = colors.listIterator();
        while (listIterator.hasNext()) {
            System.out.print(listIterator.next() + " ");
        }
        System.out.println();

        System.out.print("ListIterator (backward): ");
        while (listIterator.hasPrevious()) {
            System.out.print(listIterator.previous() + " ");
        }
        System.out.println();

        // 5. forEach with lambda
        System.out.print("forEach lambda: ");
        colors.forEach(color -> System.out.print(color + " "));
        System.out.println("\n");
    }

    private static void demonstratePerformance() {
        System.out.println("7. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        LinkedList<Integer> linkedList = new LinkedList<>();
        java.util.ArrayList<Integer> arrayList = new java.util.ArrayList<>();

        // Adding at end - LinkedList O(1), ArrayList O(1) amortized
        long start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            linkedList.add(i);
        }
        long end = System.nanoTime();
        System.out.println("LinkedList - Add 10,000 at end: " + (end - start) / 1000 + " μs");

        start = System.nanoTime();
        for (int i = 0; i < 10000; i++) {
            arrayList.add(i);
        }
        end = System.nanoTime();
        System.out.println("ArrayList - Add 10,000 at end: " + (end - start) / 1000 + " μs");

        // Adding at beginning - LinkedList O(1), ArrayList O(n)
        LinkedList<Integer> ll2 = new LinkedList<>();
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            ll2.addFirst(i);
        }
        end = System.nanoTime();
        System.out.println("LinkedList - Add 1,000 at beginning: " + (end - start) / 1000 + " μs (FAST)");

        java.util.ArrayList<Integer> al2 = new java.util.ArrayList<>();
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            al2.add(0, i);
        }
        end = System.nanoTime();
        System.out.println("ArrayList - Add 1,000 at beginning: " + (end - start) / 1000 + " μs (SLOW)");

        // Random access - LinkedList O(n), ArrayList O(1)
        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            int val = linkedList.get(i);
        }
        end = System.nanoTime();
        System.out.println("LinkedList - Get 1,000 elements: " + (end - start) / 1000 + " μs (SLOW)");

        start = System.nanoTime();
        for (int i = 0; i < 1000; i++) {
            int val = arrayList.get(i);
        }
        end = System.nanoTime();
        System.out.println("ArrayList - Get 1,000 elements: " + (end - start) / 1000 + " μs (FAST)");

        System.out.println();
    }

    private static void demonstrateAdvancedOperations() {
        System.out.println("8. ADVANCED OPERATIONS");
        System.out.println("----------------------");

        LinkedList<String> list = new LinkedList<>(List.of("A", "B", "C", "D", "E"));
        System.out.println("Original: " + list);

        // removeFirstOccurrence and removeLastOccurrence
        LinkedList<String> duplicates = new LinkedList<>(List.of("A", "B", "A", "C", "A"));
        duplicates.removeFirstOccurrence("A");
        System.out.println("After removeFirstOccurrence('A'): " + duplicates);
        duplicates.removeLastOccurrence("A");
        System.out.println("After removeLastOccurrence('A'): " + duplicates);

        // Clone - shallow copy
        @SuppressWarnings("unchecked")
        LinkedList<String> cloned = (LinkedList<String>) list.clone();
        cloned.add("F");
        System.out.println("Original: " + list);
        System.out.println("Cloned: " + cloned);

        // toArray
        String[] array = list.toArray(new String[0]);
        System.out.print("To array: ");
        for (String s : array) {
            System.out.print(s + " ");
        }
        System.out.println();

        // Null elements are allowed
        LinkedList<String> withNulls = new LinkedList<>();
        withNulls.add(null);
        withNulls.add("X");
        withNulls.add(null);
        System.out.println("List with nulls: " + withNulls);

        System.out.println("\n=== End of LinkedList Example ===");
    }
}
