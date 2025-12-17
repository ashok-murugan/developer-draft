package com.ashokmurugan.collections.concurrent;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.concurrent.TimeUnit;

/**
 * BlockingQueue Example - Thread-Safe Producer-Consumer Queue
 * 
 * EXPLANATION:
 * BlockingQueue is a thread-safe queue that supports operations that wait for
 * the queue to become non-empty when retrieving and wait for space to become
 * available when storing elements.
 * 
 * KEY CHARACTERISTICS:
 * - Thread-safe without external synchronization
 * - Blocking operations (put/take) wait when full/empty
 * - Timed operations with timeout support
 * - Multiple implementations for different use cases
 * - Perfect for producer-consumer patterns
 * 
 * IMPLEMENTATIONS:
 * 1. ArrayBlockingQueue - Bounded, array-based, FIFO
 * 2. LinkedBlockingQueue - Optionally bounded, linked nodes, FIFO
 * 3. PriorityBlockingQueue - Unbounded, heap-based, priority order
 * 4. DelayQueue - Unbounded, delayed elements
 * 5. SynchronousQueue - No capacity, direct handoff
 * 
 * OPERATIONS:
 * - put(e): Blocks if full
 * - take(): Blocks if empty
 * - offer(e): Returns false if full
 * - poll(): Returns null if empty
 * - offer(e, timeout): Waits with timeout
 * - poll(timeout): Waits with timeout
 * 
 * TIME COMPLEXITY (ArrayBlockingQueue):
 * - put(E) : O(1) - may block
 * - take() : O(1) - may block
 * - offer(E) : O(1) - non-blocking
 * - poll() : O(1) - non-blocking
 * - peek() : O(1) - non-blocking
 * - size() : O(1)
 * - contains(E) : O(n)
 * - remove(E) : O(n)
 * 
 * SPACE COMPLEXITY: O(capacity) for bounded queues
 * 
 * WHEN TO USE:
 * ✓ Producer-consumer patterns
 * ✓ Thread pool task queues
 * ✓ Rate limiting / throttling
 * ✓ Work distribution across threads
 * ✓ Buffering between processing stages
 * ✗ Need random access (use List instead)
 * ✗ Need sorted access (use PriorityQueue for single-threaded)
 */
public class BlockingQueueExample {

    public static void main(String[] args) throws InterruptedException {
        System.out.println("=== BlockingQueue Comprehensive Example ===\n");

        // 1. ArrayBlockingQueue - Bounded FIFO
        demonstrateArrayBlockingQueue();

        // 2. LinkedBlockingQueue - Optionally Bounded
        demonstrateLinkedBlockingQueue();

        // 3. PriorityBlockingQueue - Priority Order
        demonstratePriorityBlockingQueue();

        // 4. Producer-Consumer Pattern
        demonstrateProducerConsumer();

        // 5. Timeout Operations
        demonstrateTimeoutOperations();

        // 6. Practical Use Cases
        demonstratePracticalUseCases();

        // 7. Performance Comparison
        demonstratePerformance();

        // 8. Best Practices
        demonstrateBestPractices();
    }

    private static void demonstrateArrayBlockingQueue() throws InterruptedException {
        System.out.println("1. ARRAYBLOCKINGQUEUE - BOUNDED FIFO");
        System.out.println("-------------------------------------");

        // Create bounded queue with capacity 3
        BlockingQueue<String> queue = new ArrayBlockingQueue<>(3);

        System.out.println("Created ArrayBlockingQueue with capacity 3");

        // put() - blocks if full
        queue.put("Task1");
        queue.put("Task2");
        queue.put("Task3");
        System.out.println("After 3 puts: " + queue);
        System.out.println("Queue is full: " + (queue.remainingCapacity() == 0));

        // offer() - returns false if full (non-blocking)
        boolean added = queue.offer("Task4");
        System.out.println("\noffer('Task4') when full: " + added);

        // take() - blocks if empty
        String task = queue.take();
        System.out.println("take(): " + task);
        System.out.println("After take: " + queue);

        // Now we can add
        queue.put("Task4");
        System.out.println("After put('Task4'): " + queue);

        // poll() - returns null if empty (non-blocking)
        String polled = queue.poll();
        System.out.println("\npoll(): " + polled);

        // peek() - view without removing
        String peeked = queue.peek();
        System.out.println("peek(): " + peeked);
        System.out.println("After peek: " + queue + " (unchanged)");

        System.out.println();
    }

    private static void demonstrateLinkedBlockingQueue() throws InterruptedException {
        System.out.println("2. LINKEDBLOCKINGQUEUE - OPTIONALLY BOUNDED");
        System.out.println("--------------------------------------------");

        // Unbounded queue
        BlockingQueue<Integer> unbounded = new LinkedBlockingQueue<>();
        System.out.println("Unbounded LinkedBlockingQueue:");

        for (int i = 1; i <= 5; i++) {
            unbounded.put(i);
        }
        System.out.println("  Added 5 elements: " + unbounded);
        System.out.println("  Remaining capacity: " + unbounded.remainingCapacity() + " (Integer.MAX_VALUE)");

        // Bounded queue
        BlockingQueue<Integer> bounded = new LinkedBlockingQueue<>(3);
        System.out.println("\nBounded LinkedBlockingQueue (capacity 3):");

        bounded.put(1);
        bounded.put(2);
        bounded.put(3);
        System.out.println("  After 3 puts: " + bounded);
        System.out.println("  Remaining capacity: " + bounded.remainingCapacity());

        // Characteristics
        System.out.println("\nLinkedBlockingQueue characteristics:");
        System.out.println("  ✓ Two locks (putLock, takeLock) - better concurrency");
        System.out.println("  ✓ Can be bounded or unbounded");
        System.out.println("  ✓ FIFO ordering");
        System.out.println("  ✓ Higher throughput than ArrayBlockingQueue");

        System.out.println();
    }

    private static void demonstratePriorityBlockingQueue() throws InterruptedException {
        System.out.println("3. PRIORITYBLOCKINGQUEUE - PRIORITY ORDER");
        System.out.println("-----------------------------------------");

        // Priority queue with natural ordering
        BlockingQueue<Integer> pq = new PriorityBlockingQueue<>();

        // Add elements in random order
        pq.put(5);
        pq.put(1);
        pq.put(3);
        pq.put(2);
        pq.put(4);

        System.out.println("Added: 5, 1, 3, 2, 4");
        System.out.println("Queue (internal order): " + pq);

        // Take elements - comes out in priority order
        System.out.print("Taking elements: ");
        while (!pq.isEmpty()) {
            System.out.print(pq.take() + " ");
        }
        System.out.println("(sorted order)");

        // Custom priority
        class Task implements Comparable<Task> {
            String name;
            int priority;

            Task(String name, int priority) {
                this.name = name;
                this.priority = priority;
            }

            @Override
            public int compareTo(Task other) {
                return Integer.compare(this.priority, other.priority);
            }

            @Override
            public String toString() {
                return name + "(P" + priority + ")";
            }
        }

        BlockingQueue<Task> taskQueue = new PriorityBlockingQueue<>();
        taskQueue.put(new Task("Email", 3));
        taskQueue.put(new Task("Bug Fix", 1));
        taskQueue.put(new Task("Meeting", 2));

        System.out.println("\nTask queue: " + taskQueue);
        System.out.print("Processing by priority: ");
        while (!taskQueue.isEmpty()) {
            System.out.print(taskQueue.take() + " ");
        }
        System.out.println();

        System.out.println();
    }

    private static void demonstrateProducerConsumer() throws InterruptedException {
        System.out.println("4. PRODUCER-CONSUMER PATTERN");
        System.out.println("-----------------------------");

        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(5);

        // Producer thread
        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 10; i++) {
                    queue.put(i);
                    System.out.println("  Produced: " + i + " (queue size: " + queue.size() + ")");
                    Thread.sleep(100); // Simulate work
                }
                queue.put(-1); // Poison pill to stop consumer
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        // Consumer thread
        Thread consumer = new Thread(() -> {
            try {
                while (true) {
                    Integer item = queue.take();
                    if (item == -1)
                        break; // Poison pill
                    System.out.println("    Consumed: " + item + " (queue size: " + queue.size() + ")");
                    Thread.sleep(150); // Simulate slower processing
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });

        System.out.println("Starting producer-consumer...");
        producer.start();
        consumer.start();

        producer.join();
        consumer.join();

        System.out.println("Producer-consumer completed");
        System.out.println();
    }

    private static void demonstrateTimeoutOperations() throws InterruptedException {
        System.out.println("5. TIMEOUT OPERATIONS");
        System.out.println("---------------------");

        BlockingQueue<String> queue = new ArrayBlockingQueue<>(2);

        // offer with timeout
        queue.offer("Item1");
        queue.offer("Item2");
        System.out.println("Queue: " + queue + " (full)");

        boolean added = queue.offer("Item3", 1, TimeUnit.SECONDS);
        System.out.println("offer('Item3', 1 sec) when full: " + added + " (timeout)");

        // poll with timeout
        String item = queue.poll(1, TimeUnit.SECONDS);
        System.out.println("poll(1 sec): " + item);

        // Now we can add
        added = queue.offer("Item3", 1, TimeUnit.SECONDS);
        System.out.println("offer('Item3', 1 sec) after space: " + added);
        System.out.println("Queue: " + queue);

        // poll from full queue
        queue.poll();
        queue.poll();
        System.out.println("\nQueue after polling all: " + queue);

        item = queue.poll(1, TimeUnit.SECONDS);
        System.out.println("poll(1 sec) when empty: " + item + " (timeout)");

        System.out.println();
    }

    private static void demonstratePracticalUseCases() throws InterruptedException {
        System.out.println("6. PRACTICAL USE CASES");
        System.out.println("----------------------");

        // Use Case 1: Thread Pool Task Queue
        System.out.println("Use Case 1: Thread Pool Task Queue");
        BlockingQueue<Runnable> taskQueue = new LinkedBlockingQueue<>(100);

        // Simulate adding tasks
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            taskQueue.offer(() -> System.out.println("  Executing task " + taskId));
        }
        System.out.println("  Task queue size: " + taskQueue.size());

        // Use Case 2: Rate Limiting
        System.out.println("\nUse Case 2: Rate Limiting (max 3 concurrent)");
        BlockingQueue<String> permits = new ArrayBlockingQueue<>(3);
        permits.put("permit1");
        permits.put("permit2");
        permits.put("permit3");

        System.out.println("  Available permits: " + permits.size());
        String permit = permits.take();
        System.out.println("  Acquired permit: " + permit);
        System.out.println("  Remaining permits: " + permits.size());
        permits.put(permit); // Return permit
        System.out.println("  Returned permit, available: " + permits.size());

        // Use Case 3: Event Processing Pipeline
        System.out.println("\nUse Case 3: Event Processing Pipeline");
        BlockingQueue<String> events = new LinkedBlockingQueue<>();
        events.put("UserLogin");
        events.put("PageView");
        events.put("Purchase");

        System.out.println("  Events to process: " + events);
        while (!events.isEmpty()) {
            String event = events.poll();
            System.out.println("  Processing: " + event);
        }

        System.out.println();
    }

    private static void demonstratePerformance() throws InterruptedException {
        System.out.println("7. PERFORMANCE COMPARISON");
        System.out.println("-------------------------");

        int operations = 100000;

        // ArrayBlockingQueue
        BlockingQueue<Integer> abq = new ArrayBlockingQueue<>(operations);
        long start = System.nanoTime();
        for (int i = 0; i < operations; i++) {
            abq.offer(i);
        }
        for (int i = 0; i < operations; i++) {
            abq.poll();
        }
        long abqTime = (System.nanoTime() - start) / 1000000;
        System.out.println("ArrayBlockingQueue: " + abqTime + " ms");

        // LinkedBlockingQueue
        BlockingQueue<Integer> lbq = new LinkedBlockingQueue<>();
        start = System.nanoTime();
        for (int i = 0; i < operations; i++) {
            lbq.offer(i);
        }
        for (int i = 0; i < operations; i++) {
            lbq.poll();
        }
        long lbqTime = (System.nanoTime() - start) / 1000000;
        System.out.println("LinkedBlockingQueue: " + lbqTime + " ms");

        System.out.println("\nLinkedBlockingQueue characteristics:");
        System.out.println("  ✓ Two locks (better concurrency)");
        System.out.println("  ✓ No fixed capacity overhead");
        System.out.println("  ✗ More memory per element (node overhead)");

        System.out.println();
    }

    private static void demonstrateBestPractices() {
        System.out.println("8. BEST PRACTICES");
        System.out.println("-----------------");

        System.out.println("✓ DO: Use for producer-consumer patterns");
        System.out.println("  BlockingQueue<Task> queue = new LinkedBlockingQueue<>();");

        System.out.println("\n✓ DO: Choose appropriate capacity");
        System.out.println("  - Too small: Producers block frequently");
        System.out.println("  - Too large: Memory waste");
        System.out.println("  - Rule of thumb: 2-10x expected concurrent items");

        System.out.println("\n✓ DO: Use poison pill to stop consumers");
        System.out.println("  queue.put(POISON_PILL); // Special sentinel value");

        System.out.println("\n✓ DO: Handle InterruptedException properly");
        System.out.println("  try { queue.take(); }");
        System.out.println("  catch (InterruptedException e) {");
        System.out.println("    Thread.currentThread().interrupt();");
        System.out.println("  }");

        System.out.println("\n✓ DO: Use timeout operations for robustness");
        System.out.println("  queue.poll(timeout, TimeUnit.SECONDS);");

        System.out.println("\n✗ DON'T: Use for random access");
        System.out.println("  BlockingQueue doesn't support get(index)");

        System.out.println("\n✗ DON'T: Ignore capacity limits");
        System.out.println("  Monitor queue size to detect bottlenecks");

        System.out.println("\nChoosing implementation:");
        System.out.println("  ArrayBlockingQueue:  Fixed capacity, single lock");
        System.out.println("  LinkedBlockingQueue: Optional capacity, two locks");
        System.out.println("  PriorityBlockingQueue: Priority order, unbounded");
        System.out.println("  SynchronousQueue: Zero capacity, direct handoff");

        System.out.println("\n=== End of BlockingQueue Example ===");
    }
}
