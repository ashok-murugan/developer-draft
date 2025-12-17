# Concurrent Collections - Quick Reference

## Overview

This directory contains comprehensive examples of Java's concurrent collections from `java.util.concurrent` package. These collections are designed for multi-threaded environments and provide thread-safety without external synchronization.

## Examples Included

### 1. ConcurrentHashMap
**File**: `ConcurrentHashMapExample.java`

**Key Features**:
- Thread-safe hash map
- Fine-grained locking (per-bin)
- Lock-free reads
- No null keys or values
- Weakly consistent iterators

**Time Complexity**:
- get/put/remove: O(1) average
- Atomic operations: O(1) average

**When to Use**:
- High concurrency scenarios
- More reads than writes
- Need atomic compound operations

**Run**: `java -cp target/classes com.ashokmurugan.collections.concurrent.ConcurrentHashMapExample`

---

### 2. CopyOnWriteArrayList
**File**: `CopyOnWriteArrayListExample.java`

**Key Features**:
- Thread-safe list
- Copy-on-write semantics
- Lock-free reads
- Snapshot iterators
- High memory overhead during writes

**Time Complexity**:
- get: O(1) lock-free
- add/set/remove: O(n) - copies entire array

**When to Use**:
- Read operations >> write operations (100:1 or better)
- Event listeners
- Configuration caches
- Whitelists/blacklists

**Run**: `java -cp target/classes com.ashokmurugan.collections.concurrent.CopyOnWriteArrayListExample`

---

### 3. BlockingQueue
**File**: `BlockingQueueExample.java`

**Implementations Covered**:
- **ArrayBlockingQueue**: Bounded, array-based, FIFO
- **LinkedBlockingQueue**: Optionally bounded, linked nodes, FIFO
- **PriorityBlockingQueue**: Unbounded, heap-based, priority order

**Key Features**:
- Thread-safe queue
- Blocking operations (put/take)
- Timeout support
- Perfect for producer-consumer patterns

**Time Complexity**:
- put/take/offer/poll: O(1) for Array/LinkedBlocking
- put/take: O(log n) for PriorityBlocking

**When to Use**:
- Producer-consumer patterns
- Thread pool task queues
- Rate limiting
- Work distribution

**Run**: `java -cp target/classes com.ashokmurugan.collections.concurrent.BlockingQueueExample`

---

## Documentation

### Detailed Guide
See **[CONCURRENT_COLLECTIONS.md](../CONCURRENT_COLLECTIONS.md)** for:
- Internal structure diagrams
- Flow diagrams with ASCII art
- Concurrency mechanisms explained
- Memory layouts
- Performance comparisons
- Decision trees
- Best practices

### Visual Diagrams Included

1. **ConcurrentHashMap Structure**
   - Bin array layout
   - Node/TreeNode structure
   - Put operation flow
   - Concurrent access patterns

2. **CopyOnWriteArrayList Mechanism**
   - Copy-on-write flow
   - Snapshot iterator behavior
   - Memory usage during writes

3. **BlockingQueue Operations**
   - Producer-consumer pattern
   - Blocking behavior
   - Queue implementations comparison

## Quick Decision Guide

```
Need thread-safe collection?
│
├─ Key-Value Store?
│  └─ Use ConcurrentHashMap
│
├─ List (Read-Heavy)?
│  └─ Use CopyOnWriteArrayList
│
├─ List (Balanced Read/Write)?
│  └─ Use Collections.synchronizedList(ArrayList)
│
└─ Producer-Consumer?
   ├─ Bounded? → ArrayBlockingQueue
   ├─ Unbounded? → LinkedBlockingQueue
   └─ Priority? → PriorityBlockingQueue
```

## Performance Comparison

| Collection | Read | Write | Memory | Best For |
|------------|------|-------|--------|----------|
| ConcurrentHashMap | O(1) fast | O(1) fast | Low | General concurrent map |
| CopyOnWriteArrayList | O(1) fastest | O(n) slow | High | Read-heavy lists |
| ArrayBlockingQueue | O(1) | O(1) | Low | Bounded queues |
| LinkedBlockingQueue | O(1) | O(1) | Medium | Unbounded queues |

## Common Use Cases

### ConcurrentHashMap
- ✓ Caches
- ✓ Session stores
- ✓ Frequency counters
- ✓ Concurrent indexes

### CopyOnWriteArrayList
- ✓ Event listeners
- ✓ Configuration values
- ✓ Whitelists/blacklists
- ✓ Observer patterns

### BlockingQueue
- ✓ Thread pools
- ✓ Task queues
- ✓ Producer-consumer
- ✓ Rate limiting
- ✓ Event processing pipelines

## Best Practices

### DO ✓

1. **Use ConcurrentHashMap for caches**
   ```java
   ConcurrentHashMap<String, User> cache = new ConcurrentHashMap<>();
   cache.computeIfAbsent(userId, this::fetchFromDB);
   ```

2. **Use CopyOnWriteArrayList for listeners**
   ```java
   CopyOnWriteArrayList<Listener> listeners = new CopyOnWriteArrayList<>();
   // Iterate frequently, add/remove rarely
   ```

3. **Use BlockingQueue for producer-consumer**
   ```java
   BlockingQueue<Task> queue = new LinkedBlockingQueue<>();
   queue.put(task); // Producer
   Task t = queue.take(); // Consumer
   ```

### DON'T ✗

1. **Don't use CopyOnWriteArrayList for frequent writes**
   ```java
   // BAD: Creates array copy on each add
   for (int i = 0; i < 10000; i++) {
       cowList.add(i); // Very expensive!
   }
   ```

2. **Don't use null in ConcurrentHashMap**
   ```java
   // Throws NullPointerException
   map.put(null, value);
   map.put(key, null);
   ```

3. **Don't use synchronized wrappers for high concurrency**
   ```java
   // BAD: Poor scalability
   Map<K,V> map = Collections.synchronizedMap(new HashMap<>());
   // GOOD: Use ConcurrentHashMap instead
   ```

## Thread-Safety Mechanisms

| Collection | Mechanism |
|------------|-----------|
| ConcurrentHashMap | CAS + Fine-grained locks + Volatile |
| CopyOnWriteArrayList | ReentrantLock + Volatile + Immutable snapshots |
| BlockingQueue | ReentrantLock + Conditions |

## Key Differences from Regular Collections

| Feature | Regular | Concurrent |
|---------|---------|------------|
| Thread-safe | ✗ | ✓ |
| Null elements | Usually ✓ | ConcurrentHashMap ✗, others ✓ |
| Iterators | Fail-fast | Weakly consistent |
| Performance | Faster (single-thread) | Optimized for concurrency |
| Memory | Lower | Slightly higher |

## Running All Examples

```bash
# Compile
mvn clean compile

# Run ConcurrentHashMap example
java -cp target/classes com.ashokmurugan.collections.concurrent.ConcurrentHashMapExample

# Run CopyOnWriteArrayList example
java -cp target/classes com.ashokmurugan.collections.concurrent.CopyOnWriteArrayListExample

# Run BlockingQueue example
java -cp target/classes com.ashokmurugan.collections.concurrent.BlockingQueueExample
```

## Learning Path

1. **Start with ConcurrentHashMap** - Most commonly used
2. **Understand CopyOnWriteArrayList** - Learn copy-on-write pattern
3. **Study BlockingQueue** - Master producer-consumer pattern
4. **Read CONCURRENT_COLLECTIONS.md** - Deep dive into internals

## Additional Resources

- **CONCURRENT_COLLECTIONS.md**: Detailed documentation with diagrams
- **Java Concurrency in Practice**: Book by Brian Goetz
- **Java Documentation**: Official java.util.concurrent package docs

---

**Author**: Ashok Murugan  
**Last Updated**: December 2025
