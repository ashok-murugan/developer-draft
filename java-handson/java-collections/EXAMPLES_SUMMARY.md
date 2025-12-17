# Java Collections Framework - Examples Summary

## Project Overview

This project contains comprehensive examples of all major Java Collections Framework data structures with:
- ✅ Detailed explanations of internal structure
- ✅ Time complexity analysis for all operations
- ✅ Space complexity information
- ✅ Practical use cases and examples
- ✅ Performance comparisons
- ✅ Best practices and when to use each collection

## Examples Included

### 📋 List Interface (4 implementations)

#### 1. ArrayList
**File**: `src/main/java/com/ashok/collections/list/ArrayListExample.java`

**Key Points**:
- Dynamic array implementation
- Fast random access O(1)
- Slow insertions/deletions in middle O(n)
- Not thread-safe
- Grows by 1.5x when full

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Bulk Operations
4. Iteration Methods
5. Search Operations
6. Sorting and Manipulation
7. Performance Characteristics
8. Edge Cases

**Run**: `java -cp target/classes com.ashokmurugan.collections.list.ArrayListExample`

---

#### 2. LinkedList
**File**: `src/main/java/com/ashok/collections/list/LinkedListExample.java`

**Key Points**:
- Doubly-linked list implementation
- Fast insertions/deletions at ends O(1)
- Slow random access O(n)
- Implements List, Deque, Queue
- More memory overhead than ArrayList

**Sections Covered**:
1. Creation and Initialization
2. List Operations
3. Deque Operations (Double-Ended Queue)
4. Queue Operations (FIFO)
5. Stack Operations (LIFO)
6. Iteration Methods
7. Performance Comparison with ArrayList
8. Advanced Operations

**Run**: `java -cp target/classes com.ashokmurugan.collections.list.LinkedListExample`

---

#### 3. Vector
**File**: `src/main/java/com/ashok/collections/list/VectorExample.java`

**Key Points**:
- Legacy synchronized ArrayList
- Thread-safe but slower
- Grows by 2x when full
- Use ArrayList + Collections.synchronizedList() instead

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Vector-Specific Methods
4. Enumeration (Legacy Iterator)
5. Thread Safety Demonstration
6. Capacity Management
7. Performance Comparison with ArrayList
8. When to Use Vector

**Run**: `java -cp target/classes com.ashokmurugan.collections.list.VectorExample`

---

### 🔢 Set Interface (4 implementations)

#### 4. HashSet
**File**: `src/main/java/com/ashok/collections/set/HashSetExample.java`

**Key Points**:
- Hash table based set
- Fast operations O(1) average
- No order guarantee
- Allows one null element
- Uses HashMap internally

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Set Operations (Union, Intersection, Difference)
4. Iteration Methods
5. Null Handling
6. HashCode and Equals Importance
7. Performance Characteristics
8. Practical Use Cases

**Run**: `java -cp target/classes com.ashokmurugan.collections.set.HashSetExample`

---

#### 5. LinkedHashSet
**File**: `src/main/java/com/ashok/collections/set/LinkedHashSetExample.java`

**Key Points**:
- HashSet + insertion order
- Maintains predictable iteration order
- Slightly slower than HashSet
- Faster iteration than HashSet
- Uses LinkedHashMap internally

**Sections Covered**:
1. Creation and Initialization
2. Insertion Order Preservation
3. Basic Operations
4. Comparison with HashSet
5. Iteration Performance
6. Practical Use Cases (LRU-like behavior)

**Run**: `java -cp target/classes com.ashokmurugan.collections.set.LinkedHashSetExample`

---

#### 6. TreeSet
**File**: `src/main/java/com/ashok/collections/set/TreeSetExample.java`

**Key Points**:
- Red-Black tree based sorted set
- Elements in sorted order
- O(log n) operations
- No null elements allowed
- Provides navigation operations

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Navigation Operations (higher, lower, ceiling, floor)
4. Range View Operations (headSet, tailSet, subSet)
5. Custom Comparator
6. Iteration Methods
7. Performance Comparison with HashSet
8. Practical Use Cases (Leaderboards, Range Queries)

**Run**: `java -cp target/classes com.ashokmurugan.collections.set.TreeSetExample`

---

### 🗺️ Map Interface (3 implementations)

#### 7. HashMap
**File**: `src/main/java/com/ashok/collections/map/HashMapExample.java`

**Key Points**:
- Hash table based map
- Fast operations O(1) average
- No order guarantee
- Allows one null key, multiple null values
- Converts to tree when bucket has >8 elements (Java 8+)

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Advanced Operations (Java 8+: compute, merge, etc.)
4. Iteration Methods
5. Null Handling
6. HashCode and Equals for Keys
7. Performance Characteristics
8. Practical Use Cases (Frequency counting, Caching, Two-sum)

**Run**: `java -cp target/classes com.ashokmurugan.collections.map.HashMapExample`

---

#### 8. TreeMap
**File**: `src/main/java/com/ashok/collections/map/TreeMapExample.java`

**Key Points**:
- Red-Black tree based sorted map
- Keys in sorted order
- O(log n) operations
- No null keys allowed
- Provides navigation operations

**Sections Covered**:
1. Creation and Initialization
2. Basic Operations
3. Navigation Operations (higherKey, lowerKey, etc.)
4. Range View Operations (headMap, tailMap, subMap)
5. Custom Comparator
6. Iteration Methods
7. Performance Comparison with HashMap
8. Practical Use Cases (Time-series, Leaderboards, Event scheduling)

**Run**: `java -cp target/classes com.ashokmurugan.collections.map.TreeMapExample`

---

### 📬 Queue Interface (1 implementation)

#### 9. PriorityQueue
**File**: `src/main/java/com/ashok/collections/queue/PriorityQueueExample.java`

**Key Points**:
- Binary heap based priority queue
- Min-heap by default
- O(log n) insert/delete, O(1) peek
- No null elements allowed
- Not FIFO - priority based

**Sections Covered**:
1. Creation and Initialization
2. Min-Heap Operations
3. Max-Heap Operations
4. Custom Comparator
5. Queue Operations
6. Iteration (Unordered!)
7. Practical Use Cases (K largest, Merge K sorted arrays, Task scheduling)
8. Performance Characteristics

**Run**: `java -cp target/classes com.ashokmurugan.collections.queue.PriorityQueueExample`

---

## Quick Reference

### Running All Examples

```bash
# Compile the project
mvn clean compile

# Run individual examples
java -cp target/classes com.ashokmurugan.collections.list.ArrayListExample
java -cp target/classes com.ashokmurugan.collections.list.LinkedListExample
java -cp target/classes com.ashokmurugan.collections.list.VectorExample
java -cp target/classes com.ashokmurugan.collections.set.HashSetExample
java -cp target/classes com.ashokmurugan.collections.set.LinkedHashSetExample
java -cp target/classes com.ashokmurugan.collections.set.TreeSetExample
java -cp target/classes com.ashokmurugan.collections.map.HashMapExample
java -cp target/classes com.ashokmurugan.collections.map.TreeMapExample
java -cp target/classes com.ashokmurugan.collections.queue.PriorityQueueExample
```

### Quick Decision Guide

**Need a List?**
- Random access? → **ArrayList**
- Frequent insertions at ends? → **LinkedList**
- Thread-safe? → **Vector** (or Collections.synchronizedList(ArrayList))

**Need a Set?**
- Fastest operations? → **HashSet**
- Maintain insertion order? → **LinkedHashSet**
- Need sorted order? → **TreeSet**

**Need a Map?**
- Fastest operations? → **HashMap**
- Maintain insertion order? → **LinkedHashMap** (not included but similar to LinkedHashSet)
- Need sorted keys? → **TreeMap**

**Need a Queue?**
- FIFO queue? → **LinkedList** or **ArrayDeque**
- Priority-based? → **PriorityQueue**
- Stack (LIFO)? → **ArrayDeque** (better than Stack class)

## Time Complexity Cheat Sheet

| Collection | Add | Remove | Get/Contains | Notes |
|------------|-----|--------|--------------|-------|
| ArrayList | O(1)* | O(n) | O(1) / O(n) | *amortized, get is O(1) |
| LinkedList | O(1) | O(1)** | O(n) / O(n) | **at ends with reference |
| Vector | O(1)* | O(n) | O(1) / O(n) | synchronized overhead |
| HashSet | O(1) | O(1) | O(1) | average case |
| LinkedHashSet | O(1) | O(1) | O(1) | average case |
| TreeSet | O(log n) | O(log n) | O(log n) | sorted |
| HashMap | O(1) | O(1) | O(1) | average case |
| TreeMap | O(log n) | O(log n) | O(log n) | sorted |
| PriorityQueue | O(log n) | O(log n) | O(1) | peek is O(1) |

## Additional Resources

- **COLLECTIONS_HIERARCHY.md**: Complete hierarchy diagrams and interface details
- **README.md**: Project overview and setup instructions
- **pom.xml**: Maven configuration

## Learning Path

1. Start with **ArrayList** and **HashMap** (most commonly used)
2. Learn **HashSet** for unique elements
3. Understand **LinkedList** for queue/deque operations
4. Study **TreeSet** and **TreeMap** for sorted collections
5. Learn **PriorityQueue** for heap-based operations
6. Explore **LinkedHashSet** for ordered unique elements
7. Review **Vector** for legacy code understanding

## Key Takeaways

1. **ArrayList vs LinkedList**: ArrayList for random access, LinkedList for insertions/deletions
2. **HashSet vs TreeSet**: HashSet for speed, TreeSet for sorted order
3. **HashMap vs TreeMap**: HashMap for speed, TreeMap for sorted keys
4. **Always override hashCode() and equals()** for custom objects in hash-based collections
5. **TreeSet/TreeMap require Comparable** or Comparator
6. **Most collections are not thread-safe** - use synchronization or concurrent collections
7. **Fail-fast iterators** throw ConcurrentModificationException if collection modified during iteration

## Author

Ashok Murugan

## License

Educational purposes - Free to use and modify
