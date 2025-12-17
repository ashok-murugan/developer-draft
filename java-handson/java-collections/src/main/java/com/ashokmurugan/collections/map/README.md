# Map Collections - Key-Value Mastery

Welcome to the Map collections guide! Maps store key-value pairs, like a real-world dictionary where you look up definitions (values) by words (keys). Let's explore Java's powerful Map implementations!

## Table of Contents
1. [HashMap - The Fast Lookup](#hashmap---the-fast-lookup)
2. [TreeMap - The Sorted Dictionary](#treemap---the-sorted-dictionary)
3. [Comparison & Decision Guide](#comparison--decision-guide)

---

## HashMap - The Fast Lookup

### What is HashMap?

HashMap is like a super-efficient filing cabinet where you can instantly find any document by its label. It uses hashing to achieve O(1) lookups!

### Internal Structure

```
HashMap Structure:
┌─────────────────────────────────────────────────┐
│         Array of Buckets (Hash Table)            │
├─────────────────────────────────────────────────┤
│  Bucket 0:  null                                 │
│  Bucket 1:  ──▶ [key:"Alice", val:30]           │
│  Bucket 2:  ──▶ [key:"Bob", val:25] ──▶         │
│                 [key:"Charlie", val:35]          │
│  Bucket 3:  null                                 │
│  Bucket 4:  ──▶ [key:"David", val:28]           │
│  ...                                             │
└─────────────────────────────────────────────────┘

Each entry contains:
- Key (must be unique)
- Value (can be duplicate)
- Hash code
- Next reference (for collisions)
```

### Visual: Put Operation

```
put("Alice", 30):

Step 1: Hash the key
"Alice" ──▶ hashCode() ──▶ 2056 ──▶ index = 2056 % 16 = 8

Step 2: Check bucket 8
Bucket[8]: empty ──▶ Create new entry

Step 3: Store entry
Bucket[8]: [key:"Alice", value:30]

put("Alice", 35):  // Update existing key

Step 1: Hash "Alice" ──▶ index 8
Step 2: Bucket[8] has "Alice"
Step 3: Update value: 30 ──▶ 35 ✅
```

### Time Complexity

| Operation | Average | Worst | Notes |
|-----------|---------|-------|-------|
| `put(K, V)` | O(1) | O(n) | Worst: all keys in one bucket |
| `get(K)` | O(1) | O(n) | Hash + equals check |
| `remove(K)` | O(1) | O(n) | Hash + remove |
| `containsKey(K)` | O(1) | O(n) | Fast lookup |
| `containsValue(V)` | O(n) | O(n) | Must check all entries |

### Java 8+ Operations

```java
HashMap<String, Integer> scores = new HashMap<>();

// computeIfAbsent - add if missing
scores.computeIfAbsent("Alice", k -> 0);

// compute - update based on current value
scores.compute("Alice", (k, v) -> v == null ? 1 : v + 1);

// merge - combine values
scores.merge("Alice", 10, Integer::sum);

// getOrDefault - safe get
int score = scores.getOrDefault("Bob", 0);

// forEach - iterate
scores.forEach((name, score) -> 
    System.out.println(name + ": " + score)
);
```

### Real-World Examples

```java
// 1. Frequency counter
HashMap<String, Integer> wordCount = new HashMap<>();
for (String word : words) {
    wordCount.merge(word, 1, Integer::sum);
}

// 2. Cache
HashMap<String, User> userCache = new HashMap<>();
User user = userCache.computeIfAbsent(userId, 
    id -> database.fetchUser(id)
);

// 3. Two-sum problem
HashMap<Integer, Integer> map = new HashMap<>();
for (int i = 0; i < nums.length; i++) {
    int complement = target - nums[i];
    if (map.containsKey(complement)) {
        return new int[]{map.get(complement), i};
    }
    map.put(nums[i], i);
}
```

**Run**: `java -cp target/classes com.ashokmurugan.collections.map.HashMapExample`

---

## TreeMap - The Sorted Dictionary

### What is TreeMap?

TreeMap keeps keys in sorted order using a Red-Black Tree. Perfect for range queries and sorted iteration!

### Internal Structure

```
TreeMap (Red-Black Tree):
                    ┌─────────┐
                    │ K:50    │ (Black)
                    │ V:"Fifty"│
                    └────┬────┘
            ┌────────────┴────────────┐
            ▼                         ▼
        ┌─────────┐              ┌─────────┐
        │ K:25    │ (Red)        │ K:75    │ (Red)
        │ V:"..."  │              │ V:"..."  │
        └────┬────┘              └────┬────┘
      ┌──────┴──────┐          ┌──────┴──────┐
      ▼             ▼          ▼             ▼
   K:10          K:40       K:60          K:90

In-order traversal gives sorted keys:
10 → 25 → 40 → 50 → 60 → 75 → 90
```

### Navigation Operations

```
TreeMap: {10:"A", 20:"B", 30:"C", 40:"D", 50:"E"}

lowerKey(30):      Returns 20  (< 30)
floorKey(35):      Returns 30  (≤ 35)
ceilingKey(35):    Returns 40  (≥ 35)
higherKey(30):     Returns 40  (> 30)

firstKey():        Returns 10
lastKey():         Returns 50

headMap(30):       {10:"A", 20:"B"}
tailMap(30):       {30:"C", 40:"D", 50:"E"}
subMap(20, 50):    {20:"B", 30:"C", 40:"D"}
```

### Time Complexity

| Operation | Time | Notes |
|-----------|------|-------|
| `put(K, V)` | O(log n) | Tree insertion |
| `get(K)` | O(log n) | Binary search |
| `remove(K)` | O(log n) | Tree deletion |
| `firstKey/lastKey` | O(log n) | Tree navigation |
| `Navigation ops` | O(log n) | Tree traversal |

### Real-World Examples

```java
// 1. Time-series data
TreeMap<LocalDateTime, Double> stockPrices = new TreeMap<>();
stockPrices.put(time1, 100.5);
stockPrices.put(time2, 101.2);

// Get prices in time range
SortedMap<LocalDateTime, Double> todayPrices = 
    stockPrices.subMap(startOfDay, endOfDay);

// 2. Leaderboard
TreeMap<Integer, String> leaderboard = new TreeMap<>(
    Collections.reverseOrder()
);
leaderboard.put(1500, "Alice");
leaderboard.put(1200, "Bob");
// Automatically sorted by score (descending)

// 3. Event scheduling
TreeMap<LocalDateTime, Event> schedule = new TreeMap<>();
schedule.put(meeting1Time, meeting1);
schedule.put(meeting2Time, meeting2);

// Next event after now
Map.Entry<LocalDateTime, Event> next = 
    schedule.ceilingEntry(LocalDateTime.now());
```

**Run**: `java -cp target/classes com.ashokmurugan.collections.map.TreeMapExample`

---

## Comparison & Decision Guide

### Feature Comparison

| Feature | HashMap | TreeMap |
|---------|---------|---------|
| **Structure** | Hash Table | Red-Black Tree |
| **Ordering** | None | Sorted by key |
| **Null keys** | One allowed | ❌ Not allowed |
| **Null values** | ✅ Allowed | ✅ Allowed |
| **Get/Put** | O(1) ⚡ | O(log n) 🐢 |
| **Navigation** | ❌ | ✅ (higher, lower, etc.) |
| **Range queries** | ❌ | ✅ (subMap, headMap, etc.) |
| **Memory** | Lower | Higher |
| **Best for** | General use | Sorted keys, ranges |

### Performance Comparison

```
Adding 100,000 entries:
HashMap:  ████ 50ms ⚡
TreeMap:  ████████ 120ms 🐢

Get operations (100,000 times):
HashMap:  ██ 20ms ⚡
TreeMap:  ████ 45ms 🐢

Sorted iteration:
HashMap:  Must sort first: ████████ 100ms
TreeMap:  Already sorted:  ████ 40ms ⚡
```

### Decision Tree

```
Need a Map?
    │
    ├─ Need sorted keys?
    │   └─ YES ──▶ TreeMap
    │
    ├─ Need range queries?
    │   └─ YES ──▶ TreeMap
    │
    └─ Just need fast lookup?
        └─ YES ──▶ HashMap (default choice!)
```

## Summary

**HashMap**: Fast, general-purpose map. Use for 95% of cases.

**TreeMap**: Sorted keys, range queries. Use when order matters.

## Running Examples

```bash
mvn clean compile

java -cp target/classes com.ashokmurugan.collections.map.HashMapExample
java -cp target/classes com.ashokmurugan.collections.map.TreeMapExample
```

## Further Reading

- [Back to Main README](../../../../../../../README.md)
- [List Collections](../list/README.md)
- [Set Collections](../set/README.md)

---

**Happy Coding!** 🚀
