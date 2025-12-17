package com.ashokmurugan.collections.queue;

import java.util.PriorityQueue;
import java.util.Comparator;
import java.util.Arrays;

/**
 * PriorityQueue Example - Min-Heap Based Priority Queue Implementation
 * 
 * EXPLANATION:
 * PriorityQueue is an unbounded priority queue based on a priority heap
 * (min-heap by default).
 * Elements are ordered according to their natural ordering or by a Comparator.
 * The head of the queue is always the least element (min-heap) or greatest
 * (max-heap with custom comparator).
 * 
 * KEY CHARACTERISTICS:
 * - Implements Queue interface
 * - Elements ordered by priority (not FIFO)
 * - Does NOT allow null elements
 * - Not synchronized (not thread-safe)
 * - Default: Min-heap (smallest element at head)
 * - Can be configured as Max-heap using Comparator.reverseOrder()
 * - Unbounded (grows as needed)
 * 
 * INTERNAL STRUCTURE:
 * - Uses array-based binary heap
 * - Complete binary tree stored in array
 * - For element at index i:
 * - Left child: 2*i + 1
 * - Right child: 2*i + 2
 * - Parent: (i-1)/2
 * - Default initial capacity: 11
 * - Grows by 50% when full (if capacity < 64) or 100% (if capacity >= 64)
 * 
 * HEAP PROPERTY (Min-Heap):
 * - Parent is always smaller than or equal to children
 * - Root is the minimum element
 * 
 * TIME COMPLEXITY:
 * - offer(E e) / add(E e) : O(log n) - insert and bubble up
 * - poll() / remove() : O(log n) - remove root and bubble down
 * - peek() / element() : O(1) - just return root
 * - remove(Object o) : O(n) - need to find element first
 * - contains(Object o) : O(n) - linear search
 * - size() : O(1)
 * 
 * SPACE COMPLEXITY: O(n) where n is the number of elements
 * 
 * WHEN TO USE:
 * ✓ Need to repeatedly access minimum (or maximum) element
 * ✓ Implementing Dijkstra's algorithm, Huffman coding
 * ✓ Task scheduling based on priority
 * ✓ Finding k largest/smallest elements
 * ✓ Merge k sorted lists
 * ✗ Need FIFO ordering (use LinkedList or ArrayDeque)
 * ✗ Need to access elements in middle (use TreeSet)
 * ✗ Need stable ordering (elements with same priority maintain insertion order)
 */
public class PriorityQueueExample {

    public static void main(String[] args) {
        System.out.println("=== PriorityQueue Comprehensive Example ===\n");

        // 1. Creation and Initialization
        demonstrateCreation();

        // 2. Basic Operations (Min-Heap)
        demonstrateMinHeap();

        // 3. Max-Heap Operations
        demonstrateMaxHeap();

        // 4. Custom Comparator
        demonstrateCustomComparator();

        // 5. Queue Operations
        demonstrateQueueOperations();

        // 6. Iteration (Unordered!)
        demonstrateIteration();

        // 7. Practical Use Cases
        demonstratePracticalUseCases();

        // 8. Performance Characteristics
        demonstratePerformance();
    }

    private static void demonstrateCreation() {
        System.out.println("1. CREATION AND INITIALIZATION");
        System.out.println("--------------------------------");

        // Default constructor - min-heap with natural ordering
        PriorityQueue<Integer> pq1 = new PriorityQueue<>();
        System.out.println("Empty PriorityQueue: " + pq1);

        // Constructor with initial capacity
        PriorityQueue<Integer> pq2 = new PriorityQueue<>(20);
        System.out.println("PriorityQueue with capacity 20: " + pq2);

        // Constructor with comparator (max-heap)
        PriorityQueue<Integer> pq3 = new PriorityQueue<>(Comparator.reverseOrder());
        pq3.addAll(Arrays.asList(5, 2, 8, 1, 9));
        System.out.println("Max-heap: " + pq3 + " (head: " + pq3.peek() + ")");

        // Constructor with collection
        PriorityQueue<Integer> pq4 = new PriorityQueue<>(Arrays.asList(5, 2, 8, 1, 9));
        System.out.println("From collection: " + pq4 + " (head: " + pq4.peek() + ")");

        System.out.println();
    }

    private static void demonstrateMinHeap() {
        System.out.println("2. BASIC OPERATIONS (Min-Heap)");
        System.out.println("-------------------------------");

        PriorityQueue<Integer> minHeap = new PriorityQueue<>();

        // Adding elements - O(log n)
        System.out.println("Adding: 5, 2, 8, 1, 9, 3");
        minHeap.offer(5);
        minHeap.offer(2);
        minHeap.offer(8);
        minHeap.offer(1);
        minHeap.offer(9);
        minHeap.offer(3);

        System.out.println("PriorityQueue: " + minHeap);
        System.out.println("Note: Internal array order, NOT sorted order!");
        System.out.println();

        // Peek - O(1) - view minimum without removing
        Integer min = minHeap.peek();
        System.out.println("Minimum element (peek): " + min);
        System.out.println("Queue after peek: " + minHeap);

        // Poll - O(log n) - remove and return minimum
        System.out.println("\nPolling elements (always gets minimum):");
        while (!minHeap.isEmpty()) {
            System.out.println("  Polled: " + minHeap.poll() + ", Remaining: " + minHeap);
        }

        System.out.println();
    }

    private static void demonstrateMaxHeap() {
        System.out.println("3. MAX-HEAP OPERATIONS");
        System.out.println("----------------------");

        // Max-heap using Comparator.reverseOrder()
        PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());

        System.out.println("Adding: 5, 2, 8, 1, 9, 3");
        maxHeap.addAll(Arrays.asList(5, 2, 8, 1, 9, 3));

        System.out.println("Max-heap: " + maxHeap);
        System.out.println("Maximum element (peek): " + maxHeap.peek());

        System.out.println("\nPolling elements (always gets maximum):");
        while (!maxHeap.isEmpty()) {
            System.out.println("  Polled: " + maxHeap.poll() + ", Remaining: " + maxHeap);
        }

        System.out.println();
    }

    private static void demonstrateCustomComparator() {
        System.out.println("4. CUSTOM COMPARATOR");
        System.out.println("--------------------");

        // Custom class
        class Task {
            String name;
            int priority; // Lower number = higher priority

            Task(String name, int priority) {
                this.name = name;
                this.priority = priority;
            }

            @Override
            public String toString() {
                return name + "(P" + priority + ")";
            }
        }

        // Priority queue ordered by priority (ascending)
        PriorityQueue<Task> taskQueue = new PriorityQueue<>(
                Comparator.comparingInt(t -> t.priority));

        taskQueue.offer(new Task("Email", 3));
        taskQueue.offer(new Task("Bug Fix", 1));
        taskQueue.offer(new Task("Meeting", 2));
        taskQueue.offer(new Task("Documentation", 4));

        System.out.println("Task queue: " + taskQueue);
        System.out.println("\nProcessing tasks by priority:");
        while (!taskQueue.isEmpty()) {
            System.out.println("  Processing: " + taskQueue.poll());
        }

        // String length comparator
        PriorityQueue<String> byLength = new PriorityQueue<>(
                Comparator.comparingInt(String::length));
        byLength.addAll(Arrays.asList("apple", "pie", "banana", "kiwi", "strawberry"));

        System.out.println("\nStrings by length:");
        while (!byLength.isEmpty()) {
            System.out.println("  " + byLength.poll());
        }

        System.out.println();
    }

    private static void demonstrateQueueOperations() {
        System.out.println("5. QUEUE OPERATIONS");
        System.out.println("-------------------");

        PriorityQueue<Integer> pq = new PriorityQueue<>();

        // offer vs add - both add element, add throws exception on failure
        pq.offer(5);
        pq.add(2);
        pq.offer(8);
        System.out.println("After offer/add: " + pq);

        // peek vs element - both return head, element throws exception if empty
        Integer head1 = pq.peek();
        Integer head2 = pq.element();
        System.out.println("peek(): " + head1);
        System.out.println("element(): " + head2);

        // poll vs remove - both remove head, remove throws exception if empty
        Integer polled = pq.poll();
        System.out.println("poll(): " + polled);
        System.out.println("After poll: " + pq);

        Integer removed = pq.remove();
        System.out.println("remove(): " + removed);
        System.out.println("After remove: " + pq);

        // contains - O(n) - linear search
        pq.addAll(Arrays.asList(1, 3, 7, 9));
        boolean has3 = pq.contains(3);
        System.out.println("\nQueue: " + pq);
        System.out.println("Contains 3: " + has3);

        // remove(Object) - O(n) - removes specific element
        boolean removed3 = pq.remove(3);
        System.out.println("Removed 3: " + removed3);
        System.out.println("After removal: " + pq);

        // size and isEmpty
        System.out.println("Size: " + pq.size());
        System.out.println("Is empty: " + pq.isEmpty());

        // clear
        pq.clear();
        System.out.println("After clear: " + pq);

        System.out.println();
    }

    private static void demonstrateIteration() {
        System.out.println("6. ITERATION (UNORDERED!)");
        System.out.println("-------------------------");

        PriorityQueue<Integer> pq = new PriorityQueue<>(Arrays.asList(5, 2, 8, 1, 9, 3));

        System.out.println("PriorityQueue: " + pq);
        System.out.println("WARNING: Iteration does NOT guarantee sorted order!");
        System.out.println();

        // Iterator - unordered
        System.out.print("Iterator: ");
        for (Integer num : pq) {
            System.out.print(num + " ");
        }
        System.out.println("(NOT sorted!)");

        // To get sorted order, poll all elements
        System.out.print("Sorted (via polling): ");
        PriorityQueue<Integer> copy = new PriorityQueue<>(pq);
        while (!copy.isEmpty()) {
            System.out.print(copy.poll() + " ");
        }
        System.out.println();

        // Stream API
        System.out.print("Stream (unordered): ");
        pq.stream().forEach(n -> System.out.print(n + " "));
        System.out.println();

        // Sorted stream
        System.out.print("Sorted stream: ");
        pq.stream().sorted().forEach(n -> System.out.print(n + " "));
        System.out.println("\n");
    }

    private static void demonstratePracticalUseCases() {
        System.out.println("7. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Find K largest elements
        Integer[] numbers = { 3, 1, 5, 12, 2, 11, 4, 8, 9, 7 };
        int k = 3;
        PriorityQueue<Integer> minHeap = new PriorityQueue<>();

        for (int num : numbers) {
            minHeap.offer(num);
            if (minHeap.size() > k) {
                minHeap.poll(); // Remove smallest
            }
        }

        System.out.println("Array: " + Arrays.toString(numbers));
        System.out.println(k + " largest elements: " + minHeap);

        // Use Case 2: Merge K sorted arrays
        System.out.println("\nMerging sorted arrays:");
        int[][] sortedArrays = {
                { 1, 4, 7 },
                { 2, 5, 8 },
                { 3, 6, 9 }
        };

        class ArrayElement {
            int value;
            int arrayIndex;
            int elementIndex;

            ArrayElement(int value, int arrayIndex, int elementIndex) {
                this.value = value;
                this.arrayIndex = arrayIndex;
                this.elementIndex = elementIndex;
            }
        }

        PriorityQueue<ArrayElement> pq = new PriorityQueue<>(
                Comparator.comparingInt(e -> e.value));

        // Add first element from each array
        for (int i = 0; i < sortedArrays.length; i++) {
            if (sortedArrays[i].length > 0) {
                pq.offer(new ArrayElement(sortedArrays[i][0], i, 0));
            }
        }

        System.out.print("Merged: ");
        while (!pq.isEmpty()) {
            ArrayElement elem = pq.poll();
            System.out.print(elem.value + " ");

            // Add next element from same array
            int nextIndex = elem.elementIndex + 1;
            if (nextIndex < sortedArrays[elem.arrayIndex].length) {
                pq.offer(new ArrayElement(
                        sortedArrays[elem.arrayIndex][nextIndex],
                        elem.arrayIndex,
                        nextIndex));
            }
        }
        System.out.println();

        // Use Case 3: Task scheduling
        class ScheduledTask {
            String name;
            int deadline;

            ScheduledTask(String name, int deadline) {
                this.name = name;
                this.deadline = deadline;
            }

            @Override
            public String toString() {
                return name + "(deadline:" + deadline + ")";
            }
        }

        PriorityQueue<ScheduledTask> scheduler = new PriorityQueue<>(
                Comparator.comparingInt(t -> t.deadline));

        scheduler.offer(new ScheduledTask("Task A", 5));
        scheduler.offer(new ScheduledTask("Task B", 2));
        scheduler.offer(new ScheduledTask("Task C", 8));
        scheduler.offer(new ScheduledTask("Task D", 1));

        System.out.println("\nTask execution order (by deadline):");
        while (!scheduler.isEmpty()) {
            System.out.println("  Execute: " + scheduler.poll());
        }

        System.out.println();
    }

    private static void demonstratePerformance() {
        System.out.println("8. PERFORMANCE CHARACTERISTICS");
        System.out.println("-------------------------------");

        PriorityQueue<Integer> pq = new PriorityQueue<>();

        // Offer operations - O(log n)
        long start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            pq.offer(i);
        }
        long end = System.nanoTime();
        System.out.println("Offer 100,000 elements: " + (end - start) / 1000000 + " ms");

        // Peek operations - O(1)
        start = System.nanoTime();
        for (int i = 0; i < 100000; i++) {
            Integer min = pq.peek();
        }
        end = System.nanoTime();
        System.out.println("Peek 100,000 times: " + (end - start) / 1000000 + " ms");

        // Poll operations - O(log n)
        start = System.nanoTime();
        for (int i = 0; i < 50000; i++) {
            pq.poll();
        }
        end = System.nanoTime();
        System.out.println("Poll 50,000 elements: " + (end - start) / 1000000 + " ms");

        System.out.println("\nPriorityQueue provides O(log n) for insert/delete");
        System.out.println("and O(1) for peek operations");

        System.out.println("\n=== End of PriorityQueue Example ===");
    }
}
