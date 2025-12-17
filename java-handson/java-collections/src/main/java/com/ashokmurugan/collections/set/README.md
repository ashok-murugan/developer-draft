# Set Collections - Understanding Uniqueness

Welcome to the Set collections guide! Sets are all about uniqueness - no duplicates allowed! Let's explore how Java implements this powerful concept and when to use each type of Set.

## Table of Contents
1. [HashSet - The Speed Demon](#hashset---the-speed-demon)
2. [LinkedHashSet - The Organized One](#linkedhashset---the-organized-one)
3. [TreeSet - The Sorted Scholar](#treeset---the-sorted-scholar)
4. [Comparison & Decision Guide](#comparison--decision-guide)

---

## HashSet - The Speed Demon

### What is HashSet?

Imagine a library where books are organized by a special code (hash) rather than alphabetically. You can find any book instantly, but they're not in any particular order. That's HashSet! It uses hashing to achieve lightning-fast operations.

### How It Works Internally

```
HashSet uses HashMap internally!

HashSet<String>  ──────▶  HashMap<String, PRESENT>
                          (value is always a dummy object)

Internal Structure:
┌─────────────────────────────────────────────────┐
│         Hash Table (Array of Buckets)            │
├─────────────────────────────────────────────────┤
│                                                  │
│  Index 0:  null                                  │
│  Index 1:  ──▶ ["Alice"] ──▶ null               │
│  Index 2:  ──▶ ["Bob"] ──▶ ["Charlie"] ──▶ null │
│  Index 3:  null                                  │
│  Index 4:  ──▶ ["David"] ──▶ null               │
│  Index 5:  null                                  │
│  ...                                             │
│  Index 15: ──▶ ["Eve"] ──▶ null                 │
│                                                  │
└─────────────────────────────────────────────────┘

Each element is placed in a bucket based on its hash code:
index = hashCode(element) % arrayLength
```

### Visual: Adding Elements

```
Step 1: Calculate hash code
"Apple" ──▶ hashCode() ──▶ 63476538
                           ↓
                    index = 63476538 % 16 = 10

Step 2: Check if element exists
Bucket[10]: empty ──▶ Add "Apple"

Step 3: Try adding duplicate
"Apple" ──▶ hashCode() ──▶ 63476538 ──▶ index 10
Bucket[10]: ["Apple"] ──▶ Already exists! ❌ Not added

Final HashSet:
┌──────────────────────────────────────┐
│ Bucket 2:  ["Banana"]                 │
│ Bucket 5:  ["Cherry"]                 │
│ Bucket 10: ["Apple"]                  │
│ Bucket 13: ["Date"]                   │
└──────────────────────────────────────┘
Iteration order: Unpredictable! 🎲
Could be: Banana, Apple, Date, Cherry
```

### Visual: Hash Collisions

```
What happens when two elements hash to the same bucket?

"Bob" ──▶ hashCode() ──▶ index 2
"Charlie" ──▶ hashCode() ──▶ index 2 (collision!)

Bucket 2 becomes a linked list:
┌────────────────────────────────────────┐
│ Bucket 2: ["Bob"] ──▶ ["Charlie"]     │
└────────────────────────────────────────┘

When searching:
1. Go to bucket 2
2. Check "Bob".equals(searchKey)? No
3. Check "Charlie".equals(searchKey)? Yes! Found!

If too many collisions (>8 elements):
Linked list converts to Red-Black Tree for better performance!
```

### The Importance of hashCode() and equals()

```java
// BAD: Forgot to override hashCode()
class Person {
    String name;
    int age;
    
    @Override
    public boolean equals(Object o) {
        Person p = (Person) o;
        return name.equals(p.name) && age == p.age;
    }
    // Missing hashCode()! 😱
}

HashSet<Person> set = new HashSet<>();
set.add(new Person("Alice", 30));
set.add(new Person("Alice", 30)); // Should be duplicate

System.out.println(set.size()); // 2 😱 (should be 1!)

// GOOD: Both methods overridden
class Person {
    String name;
    int age;
    
    @Override
    public boolean equals(Object o) {
        Person p = (Person) o;
        return name.equals(p.name) && age == p.age;
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
}

set.add(new Person("Alice", 30));
set.add(new Person("Alice", 30)); // Correctly identified as duplicate
System.out.println(set.size()); // 1 ✅
```

### Time Complexity Breakdown

| Operation | Average | Worst Case | Notes |
|-----------|---------|------------|-------|
| `add(element)` | O(1) | O(n) | Worst case: all elements in one bucket |
| `remove(element)` | O(1) | O(n) | Same as add |
| `contains(element)` | O(1) | O(n) | Hash lookup + equals check |
| `size()` | O(1) | O(1) | Stored as variable |
| `iteration` | O(n) | O(n) | Visit all buckets |

### Set Operations (Mathematical)

```
Set A = {1, 2, 3, 4, 5}
Set B = {4, 5, 6, 7, 8}

Union (A ∪ B):
┌─────────────────────────────────────┐
│ A: {1, 2, 3, 4, 5}                   │
│ B: {4, 5, 6, 7, 8}                   │
│ ─────────────────                    │
│ A ∪ B: {1, 2, 3, 4, 5, 6, 7, 8}     │
└─────────────────────────────────────┘

Intersection (A ∩ B):
┌─────────────────────────────────────┐
│ A: {1, 2, 3, 4, 5}                   │
│ B: {4, 5, 6, 7, 8}                   │
│ ─────────────────                    │
│ A ∩ B: {4, 5}                        │
└─────────────────────────────────────┘

Difference (A - B):
┌─────────────────────────────────────┐
│ A: {1, 2, 3, 4, 5}                   │
│ B: {4, 5, 6, 7, 8}                   │
│ ─────────────────                    │
│ A - B: {1, 2, 3}                     │
└─────────────────────────────────────┘
```

### When to Use HashSet

✅ **Perfect for:**
- Removing duplicates from a collection
- Fast membership testing (contains)
- When order doesn't matter
- Implementing mathematical sets

❌ **Avoid when:**
- Need to maintain insertion order (use LinkedHashSet)
- Need sorted order (use TreeSet)
- Need null elements (HashSet allows one null, but be careful)

### Real-World Example

```java
// Remove duplicates from array
Integer[] numbers = {1, 2, 3, 2, 4, 5, 3, 6, 1};
HashSet<Integer> unique = new HashSet<>(Arrays.asList(numbers));
// Result: {1, 2, 3, 4, 5, 6}

// Check for duplicates in stream
HashSet<String> seen = new HashSet<>();
for (String word : words) {
    if (!seen.add(word)) {
        System.out.println("Duplicate found: " + word);
    }
}

// Fast membership testing
HashSet<String> validUsers = new HashSet<>(Arrays.asList(
    "alice", "bob", "charlie"
));
if (validUsers.contains(username)) {
    // O(1) lookup!
    grantAccess();
}
```

**Run Example**: `java -cp target/classes com.ashokmurugan.collections.set.HashSetExample`

---

## LinkedHashSet - The Organized One

### What is LinkedHashSet?

Think of LinkedHashSet as HashSet with a memory! It remembers the order in which you added elements. It's like a library where books are organized by hash code, but there's also a rope connecting them in the order they arrived.

### How It Works Internally

```
LinkedHashSet = HashMap + Doubly-Linked List

┌─────────────────────────────────────────────────┐
│         Hash Table (for fast lookup)             │
├─────────────────────────────────────────────────┤
│  Bucket 2:  ["Banana"] ──────┐                  │
│  Bucket 5:  ["Cherry"] ──────┼──┐               │
│  Bucket 10: ["Apple"]  ──────┼──┼──┐            │
│  Bucket 13: ["Date"]   ──────┼──┼──┼──┐         │
└──────────────────────────────┼──┼──┼──┼─────────┘
                               │  │  │  │
         Linked List (for order preservation)
                               │  │  │  │
                               ▼  ▼  ▼  ▼
                    ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐
                    │Apple│─▶│Banana│─▶│Cherry│─▶│Date│
                    └─────┘  └─────┘  └─────┘  └─────┘
                      ▲                              │
                      └──────────────────────────────┘
                         (doubly-linked)

Iteration follows the linked list: Apple → Banana → Cherry → Date
```

### Visual: Insertion Order Preservation

```
Adding elements:
add("Zebra")  ──▶ Set: [Zebra]
add("Apple")  ──▶ Set: [Zebra, Apple]
add("Mango")  ──▶ Set: [Zebra, Apple, Mango]
add("Banana") ──▶ Set: [Zebra, Apple, Mango, Banana]

HashSet iteration (random):
Possible output: Apple, Zebra, Banana, Mango 🎲

LinkedHashSet iteration (insertion order):
Guaranteed output: Zebra, Apple, Mango, Banana ✅
```

### Memory Overhead

```
HashSet (1000 elements):
┌────────────────────────────────────┐
│ Hash table: ~4KB                    │
│ Elements: ~4KB                      │
│ Total: ~8KB                         │
└────────────────────────────────────┘

LinkedHashSet (1000 elements):
┌────────────────────────────────────┐
│ Hash table: ~4KB                    │
│ Elements: ~4KB                      │
│ Linked list pointers: ~8KB          │
│ Total: ~16KB (2x HashSet!)          │
└────────────────────────────────────┘
```

### Time Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| `add(element)` | O(1) | Hash + link update |
| `remove(element)` | O(1) | Hash + unlink |
| `contains(element)` | O(1) | Hash lookup |
| `iteration` | O(n) | Faster than HashSet! |

**Iteration Performance**: LinkedHashSet is actually faster for iteration than HashSet because it only visits actual elements, not empty buckets!

### When to Use LinkedHashSet

✅ **Perfect for:**
- Need unique elements + predictable iteration order
- Removing duplicates while preserving order
- LRU cache implementation
- Maintaining insertion history

❌ **Avoid when:**
- Don't care about order (use HashSet - slightly faster)
- Need sorted order (use TreeSet)
- Memory is very constrained

### Real-World Example

```java
// Remove duplicates while preserving order
String[] words = {"apple", "banana", "apple", "cherry", "banana"};
LinkedHashSet<String> unique = new LinkedHashSet<>(Arrays.asList(words));
// Result: [apple, banana, cherry] (order preserved!)

// Track visited pages in order
LinkedHashSet<String> browserHistory = new LinkedHashSet<>();
browserHistory.add("google.com");
browserHistory.add("github.com");
browserHistory.add("stackoverflow.com");
browserHistory.add("google.com"); // Duplicate, not added
// History: google.com → github.com → stackoverflow.com

// LRU-like behavior
LinkedHashSet<String> recentFiles = new LinkedHashSet<>();
void openFile(String filename) {
    recentFiles.remove(filename); // Remove if exists
    recentFiles.add(filename);     // Add at end
    if (recentFiles.size() > 10) {
        // Remove oldest (first element)
        Iterator<String> it = recentFiles.iterator();
        it.next();
        it.remove();
    }
}
```

**Run Example**: `java -cp target/classes com.ashokmurugan.collections.set.LinkedHashSetExample`

---

## TreeSet - The Sorted Scholar

### What is TreeSet?

TreeSet is the perfectionist of Sets - it keeps everything in sorted order! It uses a Red-Black Tree (a self-balancing binary search tree) to maintain elements in natural or custom order.

### How It Works Internally

```
TreeSet uses TreeMap internally!

TreeSet<Integer> = TreeMap<Integer, PRESENT>

Red-Black Tree Structure:
                    ┌────┐
                    │ 50 │ (Black)
                    └─┬──┘
            ┌─────────┴─────────┐
            ▼                   ▼
        ┌────┐              ┌────┐
        │ 25 │ (Red)        │ 75 │ (Red)
        └─┬──┘              └─┬──┘
      ┌───┴───┐          ┌───┴───┐
      ▼       ▼          ▼       ▼
   ┌────┐ ┌────┐     ┌────┐ ┌────┐
   │ 10 │ │ 40 │     │ 60 │ │ 90 │
   └────┘ └────┘     └────┘ └────┘
  (Black)(Black)    (Black)(Black)

Properties:
1. Every node is either Red or Black
2. Root is always Black
3. Red nodes can't have Red children
4. All paths from root to leaves have same number of Black nodes
5. Maintains O(log n) height
```

### Visual: Adding Elements

```
Adding to TreeSet (maintains sorted order):

add(50) ──▶ Tree:        50

add(25) ──▶ Tree:      50
                      /
                    25

add(75) ──▶ Tree:      50
                      /  \
                    25    75

add(10) ──▶ Tree:      50
                      /  \
                    25    75
                   /
                 10

Iteration always sorted: 10, 25, 50, 75 ✅
```

### Visual: Navigation Operations

```
TreeSet: {10, 20, 30, 40, 50, 60, 70, 80, 90}

lower(50):     Returns 40  (greatest element < 50)
floor(50):     Returns 50  (greatest element ≤ 50)
ceiling(55):   Returns 60  (smallest element ≥ 55)
higher(50):    Returns 60  (smallest element > 50)

┌────────────────────────────────────────────┐
│  10  20  30  40  50  60  70  80  90        │
│              ▲   ▲   ▲                     │
│              │   │   │                     │
│         lower│   │   │higher               │
│             floor│ceiling                  │
│                  │                         │
│              (searching for 50)            │
└────────────────────────────────────────────┘
```

### Visual: Range Operations

```
TreeSet: {10, 20, 30, 40, 50, 60, 70, 80, 90}

headSet(50):      {10, 20, 30, 40}
                  └──────────────┘
                  (elements < 50)

tailSet(50):      {50, 60, 70, 80, 90}
                  └────────────────────┘
                  (elements ≥ 50)

subSet(30, 70):   {30, 40, 50, 60}
                      └──────────┘
                  (30 ≤ elements < 70)
```

### Time Complexity Breakdown

| Operation | Time | Why? |
|-----------|------|------|
| `add(element)` | O(log n) | Tree traversal + rebalancing |
| `remove(element)` | O(log n) | Tree traversal + rebalancing |
| `contains(element)` | O(log n) | Binary search in tree |
| `first()` | O(log n) | Find leftmost node |
| `last()` | O(log n) | Find rightmost node |
| `higher/lower/ceiling/floor` | O(log n) | Tree navigation |
| `iteration` | O(n) | In-order traversal |

### Comparable vs Comparator

```java
// Natural ordering (Comparable)
TreeSet<Integer> numbers = new TreeSet<>();
numbers.add(5);
numbers.add(2);
numbers.add(8);
// Sorted: [2, 5, 8]

// Custom ordering (Comparator)
TreeSet<String> words = new TreeSet<>((a, b) -> b.compareTo(a));
words.add("apple");
words.add("banana");
words.add("cherry");
// Reverse sorted: [cherry, banana, apple]

// Custom class must implement Comparable or provide Comparator
class Person implements Comparable<Person> {
    String name;
    int age;
    
    @Override
    public int compareTo(Person other) {
        return Integer.compare(this.age, other.age);
    }
}

TreeSet<Person> people = new TreeSet<>();
people.add(new Person("Alice", 30));
people.add(new Person("Bob", 25));
// Sorted by age: [Bob(25), Alice(30)]
```

### When to Use TreeSet

✅ **Perfect for:**
- Need elements in sorted order
- Range queries (subSet, headSet, tailSet)
- Finding closest elements (higher, lower, ceiling, floor)
- Leaderboards, rankings
- Time-series data

❌ **Avoid when:**
- Don't need sorting (use HashSet - much faster)
- Frequent additions/removals (O(log n) vs O(1))
- Elements can't be compared

### Real-World Example

```java
// Leaderboard (sorted by score)
TreeSet<Player> leaderboard = new TreeSet<>(
    (p1, p2) -> Integer.compare(p2.score, p1.score) // Descending
);
leaderboard.add(new Player("Alice", 1000));
leaderboard.add(new Player("Bob", 1500));
leaderboard.add(new Player("Charlie", 1200));
// Order: Bob(1500), Charlie(1200), Alice(1000)

// Find players in score range
SortedSet<Player> topPlayers = leaderboard.headSet(
    new Player("", 1300)
);
// Returns: Bob(1500)

// Time-series data
TreeSet<Event> events = new TreeSet<>(
    Comparator.comparing(Event::getTimestamp)
);
events.add(new Event("Login", timestamp1));
events.add(new Event("Purchase", timestamp2));
events.add(new Event("Logout", timestamp3));
// Automatically sorted by time!

// Range query: events between 9 AM and 5 PM
SortedSet<Event> workdayEvents = events.subSet(
    new Event("", nineAM),
    new Event("", fivePM)
);
```

**Run Example**: `java -cp target/classes com.ashokmurugan.collections.set.TreeSetExample`

---

## Comparison & Decision Guide

### Quick Decision Tree

```
Need a Set?
    │
    ├─ Need sorted order?
    │   └─ YES ──▶ TreeSet
    │
    ├─ Need insertion order?
    │   └─ YES ──▶ LinkedHashSet
    │
    └─ Just need uniqueness (fastest)?
        └─ YES ──▶ HashSet
```

### Feature Comparison Table

| Feature | HashSet | LinkedHashSet | TreeSet |
|---------|---------|---------------|---------|
| **Underlying Structure** | HashMap | HashMap + LinkedList | Red-Black Tree |
| **Ordering** | None (random) | Insertion order | Sorted (natural/custom) |
| **Null elements** | One null allowed | One null allowed | ❌ Not allowed |
| **Add** | O(1) ⚡ | O(1) ⚡ | O(log n) 🐢 |
| **Remove** | O(1) ⚡ | O(1) ⚡ | O(log n) 🐢 |
| **Contains** | O(1) ⚡ | O(1) ⚡ | O(log n) 🐢 |
| **Iteration** | O(n) | O(n) faster | O(n) |
| **Memory** | Low | Medium (2x HashSet) | Medium |
| **Thread-safe** | ❌ | ❌ | ❌ |
| **Best for** | General use | Ordered uniqueness | Sorted data |

### Performance Comparison

```
Adding 100,000 elements:
HashSet:        ████ 50ms ⚡
LinkedHashSet:  █████ 60ms ⚡
TreeSet:        ████████████ 150ms 🐢

Contains check (100,000 times):
HashSet:        ██ 20ms ⚡
LinkedHashSet:  ██ 20ms ⚡
TreeSet:        ████ 40ms 🐢

Iteration (100,000 elements):
HashSet:        ████ 40ms
LinkedHashSet:  ███ 30ms ⚡ (faster!)
TreeSet:        ████ 40ms

Memory usage (100,000 elements):
HashSet:        ████ 4MB
LinkedHashSet:  ████████ 8MB
TreeSet:        ██████ 6MB
```

### Use Case Matrix

| Scenario | Recommended | Why? |
|----------|-------------|------|
| Remove duplicates | HashSet | Fastest |
| Remove duplicates + preserve order | LinkedHashSet | Maintains insertion order |
| Leaderboard | TreeSet | Auto-sorted |
| Valid user IDs | HashSet | Fast membership test |
| Browser history | LinkedHashSet | Order matters |
| Event timeline | TreeSet | Chronological order |
| Unique tags | HashSet | Order doesn't matter |
| Recent searches | LinkedHashSet | Show in order |
| Price ranges | TreeSet | Range queries |

### Mathematical Set Operations

```java
// All Set types support these operations:

Set<Integer> a = new HashSet<>(Arrays.asList(1, 2, 3, 4, 5));
Set<Integer> b = new HashSet<>(Arrays.asList(4, 5, 6, 7, 8));

// Union (A ∪ B)
Set<Integer> union = new HashSet<>(a);
union.addAll(b);
// Result: {1, 2, 3, 4, 5, 6, 7, 8}

// Intersection (A ∩ B)
Set<Integer> intersection = new HashSet<>(a);
intersection.retainAll(b);
// Result: {4, 5}

// Difference (A - B)
Set<Integer> difference = new HashSet<>(a);
difference.removeAll(b);
// Result: {1, 2, 3}

// Symmetric Difference ((A - B) ∪ (B - A))
Set<Integer> symDiff = new HashSet<>(a);
symDiff.addAll(b);
Set<Integer> temp = new HashSet<>(a);
temp.retainAll(b);
symDiff.removeAll(temp);
// Result: {1, 2, 3, 6, 7, 8}
```

## Summary

**HashSet** is your default choice - fastest and most memory-efficient for general uniqueness needs.

**LinkedHashSet** when you need to remember the order elements were added - perfect for maintaining history.

**TreeSet** when you need elements sorted automatically - ideal for rankings, leaderboards, and range queries.

## Running the Examples

```bash
# Compile
mvn clean compile

# Run HashSet example
java -cp target/classes com.ashokmurugan.collections.set.HashSetExample

# Run LinkedHashSet example
java -cp target/classes com.ashokmurugan.collections.set.LinkedHashSetExample

# Run TreeSet example
java -cp target/classes com.ashokmurugan.collections.set.TreeSetExample
```

## Further Reading

- [Back to Main README](../../../../../../../README.md)
- [Collections Hierarchy](../../../../../../../COLLECTIONS_HIERARCHY.md)
- [List Collections](../list/README.md)
- [Map Collections](../map/README.md)

---

**Happy Coding!** 🚀

*Remember: Sets are all about uniqueness. Choose HashSet for speed, LinkedHashSet for order, TreeSet for sorting!*
