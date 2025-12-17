# Queue Collections - First-In-First-Out & Priority

Welcome to the Queue collections guide! Queues are perfect for managing tasks, events, and anything that needs to be processed in order. Let's explore Java's queue implementations!

## Table of Contents
1. [PriorityQueue - The Smart Sorter](#priorityqueue---the-smart-sorter)
2. [Queue Basics](#queue-basics)
3. [Real-World Applications](#real-world-applications)

---

## PriorityQueue - The Smart Sorter

### What is PriorityQueue?

Unlike a regular queue (FIFO), PriorityQueue processes elements based on their priority! It's like a hospital emergency room - critical patients get treated first, regardless of arrival time.

### Internal Structure

```
PriorityQueue uses a Binary Heap (Min-Heap by default):

                    ┌────┐
                    │  1 │  ← Root (minimum)
                    └─┬──┘
            ┌─────────┴─────────┐
            ▼                   ▼
        ┌────┐              ┌────┐
        │  2 │              │  3 │
        └─┬──┘              └─┬──┘
      ┌───┴───┐          ┌───┴───┐
      ▼       ▼          ▼       ▼
   ┌────┐ ┌────┐     ┌────┐ ┌────┐
   │  4 │ │  5 │     │  6 │ │  7 │
   └────┘ └────┘     └────┘ └────┘

Array representation:
[1, 2, 3, 4, 5, 6, 7]
 0  1  2  3  4  5  6

Parent of index i: (i-1)/2
Left child of i:   2*i + 1
Right child of i:  2*i + 2

Heap property: parent ≤ both children (min-heap)
```

### Visual: Adding Elements

```
Adding to Min-Heap:

Initial: [1, 2, 3, 4, 5]
              1
            /   \
           2     3
          / \
         4   5

offer(0):  // Add 0 (smaller than root!)

Step 1: Add at end
              1
            /   \
           2     3
          / \   /
         4   5 0

Step 2: Bubble up (0 < 3)
              1
            /   \
           2     0
          / \   /
         4   5 3

Step 3: Bubble up (0 < 1)
              0
            /   \
           2     1
          / \   /
         4   5 3

Final: [0, 2, 1, 4, 5, 3]
```

### Visual: Removing Elements

```
Removing from Min-Heap (poll):

Initial: [1, 2, 3, 4, 5, 6]
              1
            /   \
           2     3
          / \   /
         4   5 6

poll():  // Remove minimum (1)

Step 1: Remove root, move last to root
              6
            /   \
           2     3
          / \
         4   5

Step 2: Bubble down (6 > 2, swap with smaller child)
              2
            /   \
           6     3
          / \
         4   5

Step 3: Bubble down (6 > 4, swap)
              2
            /   \
           4     3
          / \
         6   5

Final: [2, 4, 3, 6, 5]
```

### Min-Heap vs Max-Heap

```
Min-Heap (default):
offer(5, 2, 8, 1, 9)
poll() → 1 (smallest)
poll() → 2
poll() → 5
poll() → 8
poll() → 9 (largest)

Max-Heap (custom comparator):
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(
    Collections.reverseOrder()
);
offer(5, 2, 8, 1, 9)
poll() → 9 (largest)
poll() → 8
poll() → 5
poll() → 2
poll() → 1 (smallest)
```

### Time Complexity

| Operation | Time | Why? |
|-----------|------|------|
| `offer(E)` | O(log n) | Add + bubble up |
| `poll()` | O(log n) | Remove + bubble down |
| `peek()` | O(1) | Just return root |
| `remove(E)` | O(n) | Find + remove + reheap |
| `contains(E)` | O(n) | Linear search |
| `size()` | O(1) | Stored variable |

### Custom Priority Example

```java
// Task with priority
class Task implements Comparable<Task> {
    String name;
    int priority; // 1 = highest
    
    @Override
    public int compareTo(Task other) {
        return Integer.compare(this.priority, other.priority);
    }
}

PriorityQueue<Task> tasks = new PriorityQueue<>();
tasks.offer(new Task("Email", 3));
tasks.offer(new Task("Bug Fix", 1));
tasks.offer(new Task("Meeting", 2));

// Processing order: Bug Fix(1), Meeting(2), Email(3)
while (!tasks.isEmpty()) {
    Task next = tasks.poll();
    process(next); // Processes by priority!
}
```

### Real-World Applications

```java
// 1. Find K largest elements
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
for (int num : nums) {
    minHeap.offer(num);
    if (minHeap.size() > k) {
        minHeap.poll(); // Remove smallest
    }
}
// minHeap contains K largest elements

// 2. Merge K sorted arrays
PriorityQueue<Element> pq = new PriorityQueue<>(
    Comparator.comparingInt(e -> e.value)
);
// Add first element from each array
for (int i = 0; i < k; i++) {
    pq.offer(new Element(arrays[i][0], i, 0));
}

List<Integer> result = new ArrayList<>();
while (!pq.isEmpty()) {
    Element min = pq.poll();
    result.add(min.value);
    
    // Add next element from same array
    if (min.index + 1 < arrays[min.arrayNum].length) {
        pq.offer(new Element(
            arrays[min.arrayNum][min.index + 1],
            min.arrayNum,
            min.index + 1
        ));
    }
}

// 3. Task scheduling
PriorityQueue<Task> scheduler = new PriorityQueue<>(
    Comparator.comparing(Task::getDeadline)
);
scheduler.offer(new Task("Report", deadline1));
scheduler.offer(new Task("Meeting", deadline2));

// Process tasks by deadline
while (!scheduler.isEmpty()) {
    Task urgent = scheduler.poll();
    execute(urgent);
}
```

**Run**: `java -cp target/classes com.ashokmurugan.collections.queue.PriorityQueueExample`

---

## Queue Basics

### Queue Interface Operations

```
Queue Operations:

┌─────────────────────────────────────────┐
│  Operation │ Throws    │ Returns        │
│            │ Exception │ Special Value  │
├────────────┼───────────┼────────────────┤
│  Insert    │ add(e)    │ offer(e)       │
│  Remove    │ remove()  │ poll()         │
│  Examine   │ element() │ peek()         │
└─────────────────────────────────────────┘

FIFO Queue:
┌─────────────────────────────────────┐
│  offer()              poll()         │
│    ↓                    ↑            │
│  [New] ← [3] ← [2] ← [1]            │
│  (tail)            (head)            │
└─────────────────────────────────────┘

Example:
Queue<String> queue = new LinkedList<>();
queue.offer("First");
queue.offer("Second");
queue.offer("Third");

queue.poll();  // Returns "First"
queue.poll();  // Returns "Second"
queue.peek();  // Returns "Third" (doesn't remove)
```

### Deque (Double-Ended Queue)

```
Deque Operations:

┌─────────────────────────────────────┐
│  addFirst()              addLast()  │
│      ↓                      ↓       │
│    [New]                  [New]     │
│      ↓                      ↓       │
│  ┌───────────────────────────┐     │
│  │ [A] ← [B] ← [C] ← [D]     │     │
│  └───────────────────────────┘     │
│      ↑                      ↑       │
│  removeFirst()          removeLast()│
└─────────────────────────────────────┘

LinkedList implements Deque:
Deque<String> deque = new LinkedList<>();
deque.addFirst("A");  // [A]
deque.addLast("B");   // [A, B]
deque.addFirst("Z");  // [Z, A, B]
deque.removeLast();   // [Z, A]
```

---

## Real-World Applications

### 1. Task Queue

```java
Queue<Task> taskQueue = new LinkedList<>();

// Producer adds tasks
taskQueue.offer(new Task("Process payment"));
taskQueue.offer(new Task("Send email"));

// Consumer processes tasks
while (!taskQueue.isEmpty()) {
    Task task = taskQueue.poll();
    task.execute();
}
```

### 2. BFS (Breadth-First Search)

```java
Queue<Node> queue = new LinkedList<>();
Set<Node> visited = new HashSet<>();

queue.offer(startNode);
visited.add(startNode);

while (!queue.isEmpty()) {
    Node current = queue.poll();
    process(current);
    
    for (Node neighbor : current.getNeighbors()) {
        if (!visited.contains(neighbor)) {
            queue.offer(neighbor);
            visited.add(neighbor);
        }
    }
}
```

### 3. Print Queue

```java
PriorityQueue<PrintJob> printQueue = new PriorityQueue<>(
    Comparator.comparingInt(PrintJob::getPriority)
);

printQueue.offer(new PrintJob("Document", 3));
printQueue.offer(new PrintJob("Urgent Report", 1));
printQueue.offer(new PrintJob("Photo", 2));

// Prints: Urgent Report(1), Photo(2), Document(3)
while (!printQueue.isEmpty()) {
    PrintJob job = printQueue.poll();
    printer.print(job);
}
```

## Summary

**PriorityQueue**: Process elements by priority, not insertion order. Perfect for scheduling, finding top K elements, and priority-based processing.

**Regular Queue (LinkedList)**: FIFO processing. Perfect for task queues, BFS, and sequential processing.

**Deque (LinkedList)**: Double-ended queue. Can be used as Stack (LIFO) or Queue (FIFO).

## Running Examples

```bash
mvn clean compile

java -cp target/classes com.ashokmurugan.collections.queue.PriorityQueueExample
```

## Further Reading

- [Back to Main README](../../../../../../../README.md)
- [List Collections](../list/README.md)
- [Concurrent Collections](../concurrent/README.md)

---

**Happy Coding!** 🚀

*Remember: PriorityQueue for priority-based processing, LinkedList for FIFO!*
