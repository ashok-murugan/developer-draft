# Java Collections Framework - Complete Hierarchy

## Overview

The Java Collections Framework provides a unified architecture for representing and manipulating collections. It consists of:
- **Interfaces**: Abstract data types representing collections
- **Implementations**: Concrete implementations of collection interfaces
- **Algorithms**: Methods that perform useful computations (sorting, searching, etc.)

## Complete Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Iterable<E>                              │
│                              │                                   │
│                         Collection<E>                            │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
              List<E>          Set<E>          Queue<E>
                │                │                │
                │                │                │
    ┌───────────┼───────────┐    │    ┌───────────┼───────────┐
    │           │           │    │    │           │           │
ArrayList  LinkedList   Vector   │  PriorityQueue │      ArrayDeque
                         │       │                │
                       Stack     │            Deque<E>
                                 │                │
                    ┌────────────┼────────────┐   │
                    │            │            │   │
                HashSet   LinkedHashSet  SortedSet<E>
                                            │
                                        TreeSet


┌─────────────────────────────────────────────────────────────────┐
│                           Map<K,V>                               │
│                     (Not part of Collection)                     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
            HashMap        LinkedHashMap      SortedMap<K,V>
                │                                  │
            Hashtable                           TreeMap
```

## Interface Hierarchy

### 1. Collection Interface
```
Collection<E>
├── List<E>          - Ordered collection (sequence)
├── Set<E>           - No duplicates
└── Queue<E>         - FIFO or priority-based ordering
    └── Deque<E>     - Double-ended queue
```

### 2. Map Interface (Separate Hierarchy)
```
Map<K,V>
└── SortedMap<K,V>
    └── NavigableMap<K,V>
```

## Implementation Classes

### List Implementations

| Class | Underlying DS | Ordered | Duplicates | Null | Thread-Safe | Random Access |
|-------|--------------|---------|------------|------|-------------|---------------|
| **ArrayList** | Dynamic Array | ✓ | ✓ | ✓ | ✗ | ✓ (O(1)) |
| **LinkedList** | Doubly-Linked List | ✓ | ✓ | ✓ | ✗ | ✗ (O(n)) |
| **Vector** | Dynamic Array | ✓ | ✓ | ✓ | ✓ | ✓ (O(1)) |
| **Stack** | Dynamic Array | ✓ (LIFO) | ✓ | ✓ | ✓ | ✓ (O(1)) |

### Set Implementations

| Class | Underlying DS | Ordered | Sorted | Duplicates | Null | Thread-Safe |
|-------|--------------|---------|--------|------------|------|-------------|
| **HashSet** | HashMap | ✗ | ✗ | ✗ | ✓ (one) | ✗ |
| **LinkedHashSet** | HashMap + LinkedList | ✓ (insertion) | ✗ | ✗ | ✓ (one) | ✗ |
| **TreeSet** | Red-Black Tree | ✓ (sorted) | ✓ | ✗ | ✗ | ✗ |

### Queue Implementations

| Class | Underlying DS | Ordered | Duplicates | Null | Thread-Safe |
|-------|--------------|---------|------------|------|-------------|
| **PriorityQueue** | Binary Heap | ✓ (priority) | ✓ | ✗ | ✗ |
| **ArrayDeque** | Circular Array | ✓ (insertion) | ✓ | ✗ | ✗ |
| **LinkedList** | Doubly-Linked List | ✓ (insertion) | ✓ | ✓ | ✗ |

### Map Implementations

| Class | Underlying DS | Ordered | Sorted | Null Key | Null Value | Thread-Safe |
|-------|--------------|---------|--------|----------|------------|-------------|
| **HashMap** | Hash Table | ✗ | ✗ | ✓ (one) | ✓ | ✗ |
| **LinkedHashMap** | Hash Table + LinkedList | ✓ (insertion) | ✗ | ✓ (one) | ✓ | ✗ |
| **TreeMap** | Red-Black Tree | ✓ (sorted) | ✓ | ✗ | ✓ | ✗ |
| **Hashtable** | Hash Table | ✗ | ✗ | ✗ | ✗ | ✓ |

## Time Complexity Comparison

### List Operations

| Operation | ArrayList | LinkedList | Vector |
|-----------|-----------|------------|--------|
| add(E) | O(1)* | O(1) | O(1)* |
| add(i, E) | O(n) | O(n) | O(n) |
| get(i) | O(1) | O(n) | O(1) |
| set(i, E) | O(1) | O(n) | O(1) |
| remove(i) | O(n) | O(1)** | O(n) |
| contains(E) | O(n) | O(n) | O(n) |
| iterator.remove() | O(n) | O(1) | O(n) |

*Amortized  
**When node reference is known

### Set Operations

| Operation | HashSet | LinkedHashSet | TreeSet |
|-----------|---------|---------------|---------|
| add(E) | O(1) | O(1) | O(log n) |
| remove(E) | O(1) | O(1) | O(log n) |
| contains(E) | O(1) | O(1) | O(log n) |
| iteration | O(n) | O(n) | O(n) |

### Map Operations

| Operation | HashMap | LinkedHashMap | TreeMap |
|-----------|---------|---------------|---------|
| put(K, V) | O(1) | O(1) | O(log n) |
| get(K) | O(1) | O(1) | O(log n) |
| remove(K) | O(1) | O(1) | O(log n) |
| containsKey(K) | O(1) | O(1) | O(log n) |
| containsValue(V) | O(n) | O(n) | O(n) |

### Queue Operations

| Operation | PriorityQueue | ArrayDeque | LinkedList |
|-----------|---------------|------------|------------|
| offer(E) | O(log n) | O(1)* | O(1) |
| poll() | O(log n) | O(1) | O(1) |
| peek() | O(1) | O(1) | O(1) |

*Amortized

## Choosing the Right Collection

### When to Use List

**ArrayList**
- ✓ Frequent random access by index
- ✓ Iteration over elements
- ✓ Adding elements at the end
- ✗ Frequent insertions/deletions in middle

**LinkedList**
- ✓ Frequent insertions/deletions at beginning/end
- ✓ Implementing Queue or Deque
- ✗ Frequent random access by index
- ✗ Memory-constrained environments

**Vector**
- ✓ Legacy code compatibility
- ✗ New applications (use ArrayList instead)

### When to Use Set

**HashSet**
- ✓ Fast lookup/insertion/deletion
- ✓ No duplicates needed
- ✗ Need to maintain order

**LinkedHashSet**
- ✓ No duplicates + maintain insertion order
- ✓ Predictable iteration order
- ✗ Need sorted order

**TreeSet**
- ✓ No duplicates + sorted order
- ✓ Range queries (subSet, headSet, tailSet)
- ✓ Navigation operations (higher, lower, etc.)
- ✗ Need fastest operations

### When to Use Queue

**PriorityQueue**
- ✓ Need to process elements by priority
- ✓ Finding min/max repeatedly
- ✓ Implementing algorithms (Dijkstra, Huffman)
- ✗ Need FIFO ordering

**ArrayDeque**
- ✓ Need FIFO queue or LIFO stack
- ✓ Better than Stack class
- ✓ Faster than LinkedList for queue operations
- ✗ Need random access

### When to Use Map

**HashMap**
- ✓ Fast key-value lookups
- ✓ Order doesn't matter
- ✓ Caching, indexing
- ✗ Need to maintain order

**LinkedHashMap**
- ✓ Fast lookups + maintain insertion order
- ✓ LRU cache implementation
- ✗ Need sorted keys

**TreeMap**
- ✓ Need keys in sorted order
- ✓ Range queries on keys
- ✓ Navigation operations
- ✗ Need fastest operations

## Key Interfaces and Their Methods

### Collection Interface
```java
boolean add(E e)
boolean remove(Object o)
boolean contains(Object o)
int size()
boolean isEmpty()
void clear()
Iterator<E> iterator()
Object[] toArray()
```

### List Interface (extends Collection)
```java
E get(int index)
E set(int index, E element)
void add(int index, E element)
E remove(int index)
int indexOf(Object o)
int lastIndexOf(Object o)
List<E> subList(int from, int to)
```

### Set Interface (extends Collection)
```java
// Same as Collection, no additional methods
// Just enforces no duplicates
```

### Queue Interface (extends Collection)
```java
boolean offer(E e)      // add
E poll()                // remove and return head
E peek()                // view head without removing
E element()             // like peek but throws exception
E remove()              // like poll but throws exception
```

### Deque Interface (extends Queue)
```java
void addFirst(E e)
void addLast(E e)
E removeFirst()
E removeLast()
E getFirst()
E getLast()
boolean offerFirst(E e)
boolean offerLast(E e)
E pollFirst()
E pollLast()
E peekFirst()
E peekLast()
```

### Map Interface
```java
V put(K key, V value)
V get(Object key)
V remove(Object key)
boolean containsKey(Object key)
boolean containsValue(Object value)
int size()
boolean isEmpty()
void clear()
Set<K> keySet()
Collection<V> values()
Set<Map.Entry<K,V>> entrySet()
```

### SortedMap Interface (extends Map)
```java
K firstKey()
K lastKey()
SortedMap<K,V> headMap(K toKey)
SortedMap<K,V> tailMap(K fromKey)
SortedMap<K,V> subMap(K fromKey, K toKey)
Comparator<? super K> comparator()
```

### NavigableMap Interface (extends SortedMap)
```java
Map.Entry<K,V> lowerEntry(K key)
K lowerKey(K key)
Map.Entry<K,V> floorEntry(K key)
K floorKey(K key)
Map.Entry<K,V> ceilingEntry(K key)
K ceilingKey(K key)
Map.Entry<K,V> higherEntry(K key)
K higherKey(K key)
Map.Entry<K,V> firstEntry()
Map.Entry<K,V> lastEntry()
Map.Entry<K,V> pollFirstEntry()
Map.Entry<K,V> pollLastEntry()
NavigableMap<K,V> descendingMap()
NavigableSet<K> descendingKeySet()
```

## Important Notes

1. **Thread Safety**: Most collections are NOT thread-safe
   - Use `Collections.synchronizedXxx()` for thread-safe wrappers
   - Use concurrent collections (`ConcurrentHashMap`, `CopyOnWriteArrayList`, etc.)

2. **Null Elements**:
   - Most collections allow null (except TreeSet, TreeMap, PriorityQueue)
   - Hashtable doesn't allow null keys or values

3. **Fail-Fast Iterators**:
   - Most iterators are fail-fast (throw ConcurrentModificationException)
   - Use iterator.remove() for safe removal during iteration

4. **Comparable vs Comparator**:
   - TreeSet/TreeMap require elements to be Comparable OR provide a Comparator
   - Natural ordering: implement Comparable
   - Custom ordering: provide Comparator

5. **hashCode() and equals()**:
   - Must override both for custom objects used as keys in HashMap/HashSet
   - Contract: if a.equals(b), then a.hashCode() == b.hashCode()

6. **Performance Considerations**:
   - ArrayList: Better for random access
   - LinkedList: Better for insertions/deletions
   - HashMap: Fastest for lookups
   - TreeMap: Sorted keys with log(n) operations
   - PriorityQueue: Efficient min/max operations
