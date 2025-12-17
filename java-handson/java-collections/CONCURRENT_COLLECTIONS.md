# Java Concurrent Collections - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [ConcurrentHashMap](#concurrenthashmap)
3. [CopyOnWriteArrayList](#copyonwritearraylist)
4. [BlockingQueue Implementations](#blockingqueue-implementations)
5. [Comparison Table](#comparison-table)
6. [When to Use What](#when-to-use-what)

---

## Overview

Java's concurrent collections are designed for multi-threaded environments, providing thread-safety without the need for external synchronization. They offer better performance than synchronized wrappers through various mechanisms like lock striping, copy-on-write, and lock-free algorithms.

### Concurrent Collections Hierarchy

```
java.util.concurrent
├── ConcurrentMap<K,V>
│   └── ConcurrentHashMap<K,V>
│   └── ConcurrentSkipListMap<K,V>
│
├── ConcurrentNavigableMap<K,V>
│   └── ConcurrentSkipListMap<K,V>
│
├── BlockingQueue<E>
│   ├── ArrayBlockingQueue<E>
│   ├── LinkedBlockingQueue<E>
│   ├── PriorityBlockingQueue<E>
│   ├── DelayQueue<E>
│   └── SynchronousQueue<E>
│
├── BlockingDeque<E>
│   └── LinkedBlockingDeque<E>
│
├── TransferQueue<E>
│   └── LinkedTransferQueue<E>
│
└── CopyOnWriteArrayList<E>
└── CopyOnWriteArraySet<E>
```

---

## ConcurrentHashMap

### Internal Structure

```
┌─────────────────────────────────────────────────────────┐
│              ConcurrentHashMap Structure                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┐   │
│  │ Bin 0│ Bin 1│ Bin 2│ Bin 3│ Bin 4│ Bin 5│ ...  │   │
│  └──┬───┴──┬───┴──┬───┴──┬───┴──┬───┴──┬───┴──────┘   │
│     │      │      │      │      │      │                │
│     ▼      ▼      ▼      ▼      ▼      ▼                │
│   Node   Node   Tree   null   Node   Node              │
│     │      │      │             │      │                │
│     ▼      ▼      ▼             ▼      ▼                │
│   Node   Node   Tree          Node   null              │
│     │            │                                       │
│     ▼            ▼                                       │
│   null         Tree                                     │
│                                                          │
│  Each bin can be:                                       │
│  - null (empty)                                         │
│  - Single Node (one entry)                              │
│  - Linked List (multiple entries, < 8)                  │
│  - Red-Black Tree (multiple entries, >= 8)              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Concurrency Mechanism

```
┌─────────────────────────────────────────────────────────┐
│           ConcurrentHashMap Operations                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  READ Operation (get):                                   │
│  ┌────────────────────────────────────────────┐         │
│  │ 1. Compute hash                             │         │
│  │ 2. Find bin (volatile read)                 │         │
│  │ 3. Traverse bin (no lock needed)            │         │
│  │ 4. Return value                              │         │
│  └────────────────────────────────────────────┘         │
│  ⚡ Lock-free, uses volatile reads                       │
│                                                          │
│  WRITE Operation (put):                                  │
│  ┌────────────────────────────────────────────┐         │
│  │ 1. Compute hash                             │         │
│  │ 2. Find bin                                  │         │
│  │ 3. If bin empty:                             │         │
│  │    ├─ Try CAS (Compare-And-Swap)            │         │
│  │    └─ If CAS fails, retry                    │         │
│  │ 4. If bin not empty:                         │         │
│  │    ├─ synchronized(bin) { ... }              │         │
│  │    └─ Update linked list or tree             │         │
│  └────────────────────────────────────────────┘         │
│  🔒 Fine-grained locking per bin                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Put Operation Flow

```
                    put(key, value)
                          │
                          ▼
                  Compute hash(key)
                          │
                          ▼
                  Find bin index
                          │
                          ▼
                    Is bin null?
                    ╱           ╲
                  YES            NO
                   │              │
                   ▼              ▼
            Try CAS insert   synchronized(bin)
                   │              │
                   ▼              ▼
            Success?          Linked List
              ╱    ╲          or Tree?
            YES     NO           │
             │       │           ▼
             │       └──────► Insert/Update
             │                   │
             ▼                   ▼
          Return            Check size
                                │
                                ▼
                          Size >= 8?
                            ╱    ╲
                          YES     NO
                           │       │
                           ▼       ▼
                    Treeify bin  Return
```

### Time Complexity

| Operation | Average | Worst Case | Notes |
|-----------|---------|------------|-------|
| get(key) | O(1) | O(log n) | Lock-free, tree in worst case |
| put(key, value) | O(1) | O(log n) | CAS or fine-grained lock |
| remove(key) | O(1) | O(log n) | Fine-grained lock |
| containsKey(key) | O(1) | O(log n) | Lock-free |
| size() | O(1) | O(1) | Approximate count |
| putIfAbsent() | O(1) | O(log n) | Atomic operation |
| compute() | O(1) | O(log n) | Atomic operation |

### Memory Layout

```
┌─────────────────────────────────────────────────────────┐
│              Node Structure                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Node<K,V>:                                             │
│  ┌──────────────────────────────────────┐              │
│  │ final int hash                        │              │
│  │ final K key                           │              │
│  │ volatile V value                      │ ◄── volatile │
│  │ volatile Node<K,V> next               │ ◄── volatile │
│  └──────────────────────────────────────┘              │
│                                                          │
│  TreeNode<K,V> extends Node<K,V>:                      │
│  ┌──────────────────────────────────────┐              │
│  │ TreeNode<K,V> parent                  │              │
│  │ TreeNode<K,V> left                    │              │
│  │ TreeNode<K,V> right                   │              │
│  │ TreeNode<K,V> prev                    │              │
│  │ boolean red                           │              │
│  └──────────────────────────────────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Concurrent Access Pattern

```
Thread 1 (Reader)          Thread 2 (Writer)         Thread 3 (Reader)
     │                           │                          │
     │ get(key1)                 │                          │
     ├─────────────►             │                          │
     │ volatile read             │                          │
     │ return value              │                          │
     │                           │ put(key2, val)           │
     │                           ├──────────────►           │
     │                           │ CAS/Lock bin             │
     │                           │ Update                   │
     │                           │                          │ get(key3)
     │                           │                          ├────────►
     │                           │                          │ volatile
     │                           │                          │ return
     │ get(key4)                 │                          │
     ├─────────────►             │                          │
     │ No blocking!              │ Release lock             │
     │                           │                          │
     ▼                           ▼                          ▼
   
   ⚡ Readers never block readers
   ⚡ Readers never block writers (on different bins)
   ⚡ Writers only block on same bin
```

---

## CopyOnWriteArrayList

### Internal Structure

```
┌─────────────────────────────────────────────────────────┐
│         CopyOnWriteArrayList Structure                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CopyOnWriteArrayList:                                  │
│  ┌──────────────────────────────────────┐              │
│  │ final ReentrantLock lock              │              │
│  │ private volatile Object[] array       │ ◄── volatile │
│  └──────────────────────────────────────┘              │
│                │                                         │
│                ▼                                         │
│  ┌──────┬──────┬──────┬──────┬──────┐                  │
│  │ Elem │ Elem │ Elem │ Elem │ Elem │                  │
│  │  0   │  1   │  2   │  3   │  4   │                  │
│  └──────┴──────┴──────┴──────┴──────┘                  │
│                                                          │
│  All reads: Direct volatile array access (lock-free)    │
│  All writes: Create new array copy (locked)             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Copy-On-Write Mechanism

```
┌─────────────────────────────────────────────────────────┐
│              Add Operation Flow                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Before add("D"):                                       │
│  ┌──────────────────────────────────┐                  │
│  │ array (volatile) ───────┐         │                  │
│  └──────────────────────────┼────────┘                  │
│                             ▼                            │
│                    ┌───┬───┬───┐                        │
│                    │ A │ B │ C │                        │
│                    └───┴───┴───┘                        │
│                                                          │
│  During add("D"):                                       │
│  ┌──────────────────────────────────┐                  │
│  │ 1. lock.lock()                    │                  │
│  │ 2. Get current array              │                  │
│  │ 3. Create new array (size + 1)    │                  │
│  │ 4. Copy all elements               │                  │
│  │ 5. Add new element                 │                  │
│  │ 6. array = newArray (volatile)     │                  │
│  │ 7. lock.unlock()                   │                  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  Old array:        New array:                           │
│  ┌───┬───┬───┐    ┌───┬───┬───┬───┐                   │
│  │ A │ B │ C │    │ A │ B │ C │ D │                   │
│  └───┴───┴───┘    └───┴───┴───┴───┘                   │
│       ▲                    ▲                             │
│       │                    │                             │
│   Old readers      array (volatile)                     │
│   still see this   now points here                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Snapshot Iterator

```
┌─────────────────────────────────────────────────────────┐
│            Snapshot Iterator Behavior                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Time 0: Create list and iterator                       │
│  ┌──────────────────────────────────┐                  │
│  │ list = [A, B, C]                  │                  │
│  │ iterator = list.iterator()        │                  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  Iterator snapshot:                                     │
│  ┌───┬───┬───┐                                          │
│  │ A │ B │ C │  ◄── Iterator holds reference            │
│  └───┴───┴───┘                                          │
│                                                          │
│  Time 1: Modify list                                    │
│  ┌──────────────────────────────────┐                  │
│  │ list.add("D")                     │                  │
│  │ list.add("E")                     │                  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  Current list:                                          │
│  ┌───┬───┬───┬───┬───┐                                 │
│  │ A │ B │ C │ D │ E │  ◄── New array                  │
│  └───┴───┴───┴───┴───┘                                 │
│                                                          │
│  Iterator still sees:                                   │
│  ┌───┬───┬───┐                                          │
│  │ A │ B │ C │  ◄── Old snapshot                       │
│  └───┴───┴───┘                                          │
│                                                          │
│  ✓ No ConcurrentModificationException                   │
│  ✓ Iterator is immutable snapshot                       │
│  ✗ Iterator doesn't see new elements                    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Concurrent Access Pattern

```
Thread 1 (Reader)          Thread 2 (Writer)         Thread 3 (Reader)
     │                           │                          │
     │ get(0)                    │                          │
     ├─────────────►             │                          │
     │ volatile read             │                          │
     │ return value              │                          │
     │                           │ add(elem)                │
     │                           ├──────────────►           │
     │                           │ lock.lock()              │
     │                           │ Copy array               │
     │                           │ Add element              │
     │ get(1)                    │ volatile write           │
     ├─────────────►             │ lock.unlock()            │
     │ No blocking!              │                          │ get(2)
     │                           │                          ├────────►
     │                           │                          │ volatile
     │                           │                          │ return
     ▼                           ▼                          ▼
   
   ⚡ Reads NEVER block (lock-free)
   ⚡ Writes block other writes only
   ⚡ Writes NEVER block reads
```

### Time Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| get(index) | O(1) | Lock-free volatile read |
| add(E) | O(n) | Copies entire array |
| add(index, E) | O(n) | Copies entire array |
| set(index, E) | O(n) | Copies entire array |
| remove(index) | O(n) | Copies entire array |
| contains(E) | O(n) | Linear search |
| iterator() | O(1) | Returns snapshot |
| size() | O(1) | Array length |

### Memory Usage

```
┌─────────────────────────────────────────────────────────┐
│              Memory Overhead                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Steady State (no writes):                              │
│  ┌──────────────────────────────────┐                  │
│  │ Memory = n * element_size         │                  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  During Write:                                          │
│  ┌──────────────────────────────────┐                  │
│  │ Old array: n * element_size       │                  │
│  │ New array: (n+1) * element_size   │                  │
│  │ Total: (2n+1) * element_size      │ ◄── 2x memory!  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  After Write (old array GC'd):                          │
│  ┌──────────────────────────────────┐                  │
│  │ Memory = (n+1) * element_size     │                  │
│  └──────────────────────────────────┘                  │
│                                                          │
│  ⚠ Warning: Temporary 2x memory usage during writes     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## BlockingQueue Implementations

### BlockingQueue Interface

```
┌─────────────────────────────────────────────────────────┐
│           BlockingQueue Operations                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ Operation    │ Throws       │ Blocks       │        │
│  │ Type         │ Exception    │ (waits)      │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Insert       │ add(e)       │ put(e)       │        │
│  │              │ (throws)     │ (waits)      │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Remove       │ remove()     │ take()       │        │
│  │              │ (throws)     │ (waits)      │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Examine      │ element()    │ N/A          │        │
│  │              │ (throws)     │              │        │
│  └──────────────┴──────────────┴──────────────┘        │
│                                                          │
│  ┌──────────────┬──────────────┬──────────────┐        │
│  │ Operation    │ Returns      │ Times Out    │        │
│  │ Type         │ Special      │ (waits)      │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Insert       │ offer(e)     │ offer(e,t,u) │        │
│  │              │ (false)      │ (timeout)    │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Remove       │ poll()       │ poll(t,u)    │        │
│  │              │ (null)       │ (timeout)    │        │
│  ├──────────────┼──────────────┼──────────────┤        │
│  │ Examine      │ peek()       │ N/A          │        │
│  │              │ (null)       │              │        │
│  └──────────────┴──────────────┴──────────────┘        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### ArrayBlockingQueue

```
┌─────────────────────────────────────────────────────────┐
│          ArrayBlockingQueue Structure                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Fixed-size circular array:                             │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┐                     │
│  │ A │ B │ C │   │   │   │   │   │  capacity = 8       │
│  └───┴───┴───┴───┴───┴───┴───┴───┘                     │
│    ▲       ▲                                             │
│    │       │                                             │
│  takeIndex putIndex                                     │
│   (head)   (tail)                                       │
│                                                          │
│  Internal state:                                        │
│  - Object[] items (fixed size)                          │
│  - int takeIndex (next take position)                   │
│  - int putIndex (next put position)                     │
│  - int count (current size)                             │
│  - ReentrantLock lock (single lock)                     │
│  - Condition notEmpty (for take)                        │
│  - Condition notFull (for put)                          │
│                                                          │
│  Characteristics:                                       │
│  ✓ Bounded capacity                                     │
│  ✓ FIFO ordering                                        │
│  ✓ Single lock (fair or unfair)                         │
│  ✓ Blocks when full/empty                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Producer-Consumer Pattern

```
┌─────────────────────────────────────────────────────────┐
│        Producer-Consumer with BlockingQueue             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Producer Thread              BlockingQueue              │
│       │                            │                     │
│       │ put(item)                  │                     │
│       ├───────────────────────────►│                     │
│       │                            │                     │
│       │ Queue full?                │                     │
│       │   YES: Block/Wait          │                     │
│       │   NO: Add item             │                     │
│       │                            │                     │
│       │                            │  Consumer Thread    │
│       │                            │       │             │
│       │                            │◄──────┤ take()      │
│       │                            │       │             │
│       │                            │ Queue empty?        │
│       │                            │   YES: Block/Wait   │
│       │                            │   NO: Remove item   │
│       │                            │       │             │
│       │                            │       ▼             │
│       │                            │   Process item      │
│       │                            │                     │
│       ▼                            ▼                     │
│                                                          │
│  Flow:                                                   │
│  1. Producer creates items                              │
│  2. put() blocks if queue full                          │
│  3. Consumer takes items                                │
│  4. take() blocks if queue empty                        │
│  5. Automatic synchronization                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Comparison Table

### Performance Comparison

| Collection | Read | Write | Iteration | Memory | Use Case |
|------------|------|-------|-----------|--------|----------|
| **ConcurrentHashMap** | O(1) lock-free | O(1) fine-grained lock | O(n) weakly consistent | Low | High concurrency, key-value |
| **CopyOnWriteArrayList** | O(1) lock-free | O(n) full copy | O(n) snapshot | High | Read-heavy, rare writes |
| **CopyOnWriteArraySet** | O(n) lock-free | O(n) full copy | O(n) snapshot | High | Read-heavy unique elements |
| **ConcurrentSkipListMap** | O(log n) lock-free | O(log n) lock-free | O(n) weakly consistent | Medium | Sorted, concurrent |
| **ArrayBlockingQueue** | O(1) locked | O(1) locked | O(n) locked | Low | Bounded producer-consumer |
| **LinkedBlockingQueue** | O(1) two locks | O(1) two locks | O(n) locked | Medium | Unbounded producer-consumer |
| **PriorityBlockingQueue** | O(log n) locked | O(log n) locked | O(n) locked | Medium | Priority-based processing |

### Thread-Safety Mechanisms

```
┌─────────────────────────────────────────────────────────┐
│         Thread-Safety Mechanisms Comparison              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ConcurrentHashMap:                                     │
│  ┌──────────────────────────────────────┐              │
│  │ • CAS (Compare-And-Swap)              │              │
│  │ • Volatile variables                  │              │
│  │ • Fine-grained locking per bin        │              │
│  │ • Lock-free reads                     │              │
│  └──────────────────────────────────────┘              │
│                                                          │
│  CopyOnWriteArrayList:                                  │
│  ┌──────────────────────────────────────┐              │
│  │ • ReentrantLock for writes            │              │
│  │ • Volatile array reference            │              │
│  │ • Immutable snapshots                 │              │
│  │ • Lock-free reads                     │              │
│  └──────────────────────────────────────┘              │
│                                                          │
│  BlockingQueue:                                         │
│  ┌──────────────────────────────────────┐              │
│  │ • ReentrantLock(s)                    │              │
│  │ • Condition variables                 │              │
│  │ • await()/signal() for blocking       │              │
│  │ • All operations locked               │              │
│  └──────────────────────────────────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## When to Use What

### Decision Tree

```
                    Need thread-safe collection?
                              │
                              ▼
                            YES
                              │
                ┌─────────────┴─────────────┐
                │                           │
           Key-Value?                    List/Set?
                │                           │
                ▼                           ▼
         ┌──────────────┐          Read >> Write?
         │              │           ╱           ╲
    Sorted?        Unsorted       YES           NO
      ╱  ╲            │            │             │
    YES   NO          │            ▼             ▼
     │     │          │    CopyOnWriteArrayList  │
     │     │          │    CopyOnWriteArraySet   │
     │     │          │                          │
     ▼     ▼          ▼                          ▼
ConcurrentSkip  ConcurrentHashMap    Collections.synchronizedList
  ListMap                             Collections.synchronizedSet
                              
                              
            Need producer-consumer?
                    │
                    ▼
                  YES
                    │
        ┌───────────┴───────────┐
        │                       │
    Bounded?              Priority-based?
      ╱  ╲                   ╱  ╲
    YES   NO               YES   NO
     │     │                │     │
     ▼     ▼                ▼     ▼
ArrayBlocking  LinkedBlocking  PriorityBlocking  LinkedTransfer
  Queue          Queue           Queue             Queue
```

### Use Case Matrix

| Scenario | Recommended Collection | Reason |
|----------|----------------------|---------|
| **Cache** | ConcurrentHashMap | Fast concurrent reads/writes |
| **Event Listeners** | CopyOnWriteArrayList | Frequent iteration, rare add/remove |
| **Configuration** | CopyOnWriteArrayList | Read-heavy, rarely updated |
| **Task Queue** | LinkedBlockingQueue | Producer-consumer pattern |
| **Thread Pool** | LinkedBlockingQueue | Unbounded task queue |
| **Rate Limiting** | ArrayBlockingQueue | Bounded capacity |
| **Priority Tasks** | PriorityBlockingQueue | Priority-based processing |
| **Sorted Concurrent Map** | ConcurrentSkipListMap | Sorted keys, concurrent access |
| **Whitelist/Blacklist** | CopyOnWriteArraySet | Frequent checks, rare updates |
| **Session Store** | ConcurrentHashMap | Concurrent session access |

### Performance Guidelines

```
┌─────────────────────────────────────────────────────────┐
│              Performance Guidelines                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Read-Heavy (90%+ reads):                               │
│  ✓ CopyOnWriteArrayList/Set                            │
│  ✓ ConcurrentHashMap (also good)                       │
│                                                          │
│  Write-Heavy (50%+ writes):                             │
│  ✓ ConcurrentHashMap                                    │
│  ✗ CopyOnWriteArrayList (too expensive)                │
│                                                          │
│  Balanced Read/Write:                                   │
│  ✓ ConcurrentHashMap                                    │
│  ✓ Collections.synchronizedList                        │
│                                                          │
│  Need Ordering:                                         │
│  ✓ ConcurrentSkipListMap (sorted)                      │
│  ✓ CopyOnWriteArrayList (insertion order)              │
│  ✓ LinkedBlockingQueue (FIFO)                          │
│                                                          │
│  Memory Constrained:                                    │
│  ✓ ConcurrentHashMap (low overhead)                    │
│  ✗ CopyOnWriteArrayList (2x during writes)             │
│                                                          │
│  High Concurrency:                                      │
│  ✓ ConcurrentHashMap (scales well)                     │
│  ✓ ConcurrentSkipListMap (lock-free)                   │
│  ✗ Collections.synchronizedXxx (poor scaling)          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Best Practices

### DO's ✓

1. **Use ConcurrentHashMap for caches**
   ```java
   ConcurrentHashMap<String, User> cache = new ConcurrentHashMap<>();
   cache.computeIfAbsent(userId, id -> fetchFromDatabase(id));
   ```

2. **Use CopyOnWriteArrayList for listeners**
   ```java
   CopyOnWriteArrayList<EventListener> listeners = new CopyOnWriteArrayList<>();
   // Frequent iteration, rare add/remove
   ```

3. **Use BlockingQueue for producer-consumer**
   ```java
   BlockingQueue<Task> queue = new LinkedBlockingQueue<>();
   queue.put(task); // Producer
   Task t = queue.take(); // Consumer
   ```

4. **Use atomic operations**
   ```java
   map.computeIfAbsent(key, k -> expensiveOperation());
   map.merge(key, 1, Integer::sum);
   ```

### DON'Ts ✗

1. **Don't use CopyOnWriteArrayList for frequent writes**
   ```java
   // BAD: O(n) for each add
   for (int i = 0; i < 10000; i++) {
       cowList.add(i); // Creates 10,000 array copies!
   }
   ```

2. **Don't use null in ConcurrentHashMap**
   ```java
   // Throws NullPointerException
   map.put(null, value);
   map.put(key, null);
   ```

3. **Don't rely on size() during concurrent modifications**
   ```java
   // Size is approximate
   int size = concurrentMap.size(); // May not be exact
   ```

4. **Don't use synchronized wrappers for high concurrency**
   ```java
   // BAD: Poor scalability
   Map<K,V> map = Collections.synchronizedMap(new HashMap<>());
   ```

---

## Summary

### Quick Reference

| Need | Use |
|------|-----|
| Thread-safe Map | ConcurrentHashMap |
| Thread-safe List (read-heavy) | CopyOnWriteArrayList |
| Thread-safe List (balanced) | Collections.synchronizedList |
| Thread-safe Set (read-heavy) | CopyOnWriteArraySet |
| Thread-safe Sorted Map | ConcurrentSkipListMap |
| Producer-Consumer | BlockingQueue |
| Priority Queue | PriorityBlockingQueue |
| Bounded Queue | ArrayBlockingQueue |
| Unbounded Queue | LinkedBlockingQueue |

### Key Takeaways

1. **ConcurrentHashMap**: Best general-purpose concurrent map
2. **CopyOnWriteArrayList**: Only for read-heavy scenarios
3. **BlockingQueue**: Perfect for producer-consumer patterns
4. **Avoid synchronized wrappers**: Use concurrent collections instead
5. **No nulls in ConcurrentHashMap**: Design decision for safety
6. **Weakly consistent iterators**: Won't throw ConcurrentModificationException
7. **Choose based on read/write ratio**: Critical for performance

---

*For detailed examples and code, see the Java source files in the concurrent package.*
