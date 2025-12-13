# Java Collections Hands-On

A hands-on Java project for practicing custom data structures and collections implementations. This repository contains various ADT (Abstract Data Type) implementations to explore data structure design patterns and algorithms.

## Overview

This project serves as a learning platform for implementing custom collections and data structures in Java. Each implementation focuses on different aspects of data structure design, from basic operations to advanced algorithms.

## Current Implementations

### DigitList
A unique ADT that treats an integer as a mutable list of decimal digits, providing list-like operations on individual digits.

**Features:**
- **Get digit at index**: Retrieve any digit by position (0-based, left-to-right)
- **Set digit at index**: Replace a digit at a specific position
- **Add digit**: Append a digit to the end
- **Remove digit**: Remove a digit from any position
- **Size**: Get the total number of digits

**Usage Example:**
```java
DigitList dl = new DigitList(12345);

// Get digit at index
int digit = dl.get(0);  // Returns 1

// Set digit at index
dl.set(0, 9);  // Changes to 92345

// Add digit
dl.add(6);  // Changes to 923456

// Remove digit
dl.remove(0);  // Changes to 23456

// Get size
int size = dl.size();  // Returns 5
```

## Project Structure

```
handson/
├── src/
│   ├── main/
│   │   └── java/
│   │       ├── Main.java
│   │       └── com/ashokmurugan/collections/
│   │           └── digit/
│   │               └── DigitList.java
│   └── test/
│       └── java/
│           └── com/ashokmurugan/collections/
│               └── digit/
│                   └── DigitListTest.java
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── TEST_DOCUMENTATION.md
├── pom.xml
└── handson.iml
```

## Building and Running

### Prerequisites
- Java 11 or higher
- Maven 3.6 or higher

### Using Maven

```bash
# Compile the project
mvn compile

# Run the main class
mvn exec:java -Dexec.mainClass="Main"

# Package as JAR
mvn package
```

### Using IntelliJ IDEA

1. Open the project in IntelliJ IDEA
2. Maven will automatically import dependencies
3. Navigate to `Main.java`
4. Run the main method

## Testing

This project includes comprehensive JUnit 5 test cases covering all functionality.

### Running Tests with Maven

```bash
# Run all tests
mvn test

# Run tests with coverage report
mvn clean test jacoco:report

# View coverage report
open target/site/jacoco/index.html
```

### Running Tests in IntelliJ IDEA

1. Right-click on `DigitListTest.java`
2. Select "Run 'DigitListTest'"
3. View test results in the Run panel

### Test Coverage

The test suite includes **60+ test cases** covering:

- ✅ **Constructor validation** - Valid values, zero, negative numbers
- ✅ **Size operations** - Zero, single digit, multiple digits, large numbers
- ✅ **Get operations** - First, middle, last digits, boundary checks
- ✅ **Set operations** - All positions, invalid digits, index validation
- ✅ **Add operations** - Appending digits, building numbers from zero
- ✅ **Remove operations** - All positions, reducing to zero
- ✅ **Complex sequences** - Multiple operations, digit reversal
- ✅ **Edge cases** - Max int value, all zeros, all nines
- ✅ **Error handling** - All exception scenarios

## Implementation Details

### DigitList

The `DigitList` class uses mathematical operations (division, modulo, powers of 10) to manipulate digits without converting to arrays or strings, making it an efficient and educational example of:

- Custom data structure design
- Mathematical digit manipulation
- Java ADT implementation
- Index-based operations

**Constraints:**
- Only non-negative integers are supported
- Digits must be in the range 0–9
- Indexing is zero-based, left to right
- Zero is represented as `[0]`
- Removing the last digit results in `[0]`

## Future Implementations

This project will expand to include additional data structures such as:
- Custom List implementations
- Stack and Queue variants
- Tree structures
- Graph implementations
- Hash-based collections

## License

This project is open source and available for educational purposes.

## Author

Ashok Murugan
