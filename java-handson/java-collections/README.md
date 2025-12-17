# Java Collections Framework - Comprehensive Examples

This project provides comprehensive examples of all major Java Collections Framework data structures with:
- **ADT (Abstract Data Type) implementations**
- **Detailed explanations**
- **Time complexity analysis**
- **Proper hierarchy organization**

## Collections Hierarchy

```
Collection (Interface)
├── List (Interface)
│   ├── ArrayList
│   ├── LinkedList
│   └── Vector
│       └── Stack
├── Set (Interface)
│   ├── HashSet
│   ├── LinkedHashSet
│   └── SortedSet (Interface)
│       └── TreeSet
└── Queue (Interface)
    ├── PriorityQueue
    └── Deque (Interface)
        ├── ArrayDeque
        └── LinkedList

Map (Interface)
├── HashMap
├── LinkedHashMap
├── Hashtable
└── SortedMap (Interface)
    └── TreeMap
```

## Project Structure

```
src/main/java/com/ashok/collections/
├── list/           # List implementations (ArrayList, LinkedList, Vector, Stack)
├── set/            # Set implementations (HashSet, LinkedHashSet, TreeSet)
├── queue/          # Queue implementations (PriorityQueue, ArrayDeque)
├── map/            # Map implementations (HashMap, LinkedHashMap, TreeMap, Hashtable)
└── adt/            # Custom ADT implementations
```

## Examples Included

### List Interface
1. **ArrayList** - Dynamic array implementation
2. **LinkedList** - Doubly-linked list implementation
3. **Vector** - Synchronized dynamic array
4. **Stack** - LIFO stack implementation

### Set Interface
1. **HashSet** - Hash table based set
2. **LinkedHashSet** - Hash table + linked list set
3. **TreeSet** - Red-Black tree based sorted set

### Queue Interface
1. **PriorityQueue** - Heap-based priority queue
2. **ArrayDeque** - Resizable array deque
3. **LinkedList** - Also implements Queue/Deque

### Map Interface
1. **HashMap** - Hash table based map
2. **LinkedHashMap** - Hash table + linked list map
3. **TreeMap** - Red-Black tree based sorted map
4. **Hashtable** - Legacy synchronized hash table

## Time Complexity Reference

| Operation | ArrayList | LinkedList | HashSet | TreeSet | HashMap | TreeMap |
|-----------|-----------|------------|---------|---------|---------|---------|
| Add       | O(1)*     | O(1)       | O(1)    | O(log n)| O(1)    | O(log n)|
| Remove    | O(n)      | O(1)**     | O(1)    | O(log n)| O(1)    | O(log n)|
| Get       | O(1)      | O(n)       | -       | -       | O(1)    | O(log n)|
| Contains  | O(n)      | O(n)       | O(1)    | O(log n)| O(1)    | O(log n)|
| Iterate   | O(n)      | O(n)       | O(n)    | O(n)    | O(n)    | O(n)    |

*Amortized time complexity  
**When node reference is known

## Building and Running

```bash
# Compile the project
mvn clean compile

# Run tests
mvn test

# Package
mvn package
```

## Running Individual Examples

Each example class has a `main` method that can be run directly:

```bash
# Run ArrayList example
java -cp target/classes com.ashokmurugan.collections.list.ArrayListExample

# Run HashSet example
java -cp target/classes com.ashokmurugan.collections.set.HashSetExample

# And so on...
```

## Author
Ashok Murugan
