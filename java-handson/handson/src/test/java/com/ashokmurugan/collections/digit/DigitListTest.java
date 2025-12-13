package com.ashokmurugan.collections.digit;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Comprehensive test suite for DigitList ADT
 */
public class DigitListTest {

    private DigitList digitList;

    @BeforeEach
    void setUp() {
        digitList = new DigitList(12345);
    }

    /* ---------------- Constructor Tests ---------------- */

    @Test
    void testConstructorWithValidValue() {
        DigitList dl = new DigitList(12345);
        assertEquals(12345, dl.intValue());
    }

    @Test
    void testConstructorWithZero() {
        DigitList dl = new DigitList(0);
        assertEquals(0, dl.intValue());
    }

    @Test
    void testConstructorWithNegativeValueThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            new DigitList(-123);
        });
    }

    /* ---------------- Size Tests ---------------- */

    @Test
    void testSizeOfZero() {
        DigitList dl = new DigitList(0);
        assertEquals(1, dl.size());
    }

    @Test
    void testSizeOfSingleDigit() {
        DigitList dl = new DigitList(5);
        assertEquals(1, dl.size());
    }

    @Test
    void testSizeOfMultipleDigits() {
        assertEquals(5, digitList.size());
    }

    @Test
    void testSizeOfLargeNumber() {
        DigitList dl = new DigitList(987654321);
        assertEquals(9, dl.size());
    }

    /* ---------------- Get Tests ---------------- */

    @Test
    void testGetFirstDigit() {
        assertEquals(1, digitList.get(0));
    }

    @Test
    void testGetMiddleDigit() {
        assertEquals(3, digitList.get(2));
    }

    @Test
    void testGetLastDigit() {
        assertEquals(5, digitList.get(4));
    }

    @Test
    void testGetFromZero() {
        DigitList dl = new DigitList(0);
        assertEquals(0, dl.get(0));
    }

    @Test
    void testGetWithNegativeIndexThrowsException() {
        assertThrows(IndexOutOfBoundsException.class, () -> {
            digitList.get(-1);
        });
    }

    @Test
    void testGetWithIndexTooLargeThrowsException() {
        assertThrows(IndexOutOfBoundsException.class, () -> {
            digitList.get(5);
        });
    }

    /* ---------------- Set Tests ---------------- */

    @Test
    void testSetFirstDigit() {
        digitList.set(0, 9);
        assertEquals(92345, digitList.intValue());
    }

    @Test
    void testSetMiddleDigit() {
        digitList.set(2, 7);
        assertEquals(12745, digitList.intValue());
    }

    @Test
    void testSetLastDigit() {
        digitList.set(4, 0);
        assertEquals(12340, digitList.intValue());
    }

    @Test
    void testSetZeroDigit() {
        DigitList dl = new DigitList(0);
        dl.set(0, 5);
        assertEquals(5, dl.intValue());
    }

    @Test
    void testSetWithInvalidDigitThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            digitList.set(0, 10);
        });
    }

    @Test
    void testSetWithNegativeDigitThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            digitList.set(0, -1);
        });
    }

    @Test
    void testSetWithInvalidIndexThrowsException() {
        assertThrows(IndexOutOfBoundsException.class, () -> {
            digitList.set(10, 5);
        });
    }

    /* ---------------- Add Tests ---------------- */

    @Test
    void testAddDigitToEnd() {
        digitList.add(6);
        assertEquals(123456, digitList.intValue());
        assertEquals(6, digitList.size());
    }

    @Test
    void testAddMultipleDigits() {
        digitList.add(6);
        digitList.add(7);
        digitList.add(8);
        assertEquals(12345678, digitList.intValue());
    }

    @Test
    void testAddToZero() {
        DigitList dl = new DigitList(0);
        dl.add(5);
        assertEquals(5, dl.intValue());
    }

    @Test
    void testAddZeroDigit() {
        digitList.add(0);
        assertEquals(123450, digitList.intValue());
    }

    @Test
    void testAddInvalidDigitThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            digitList.add(15);
        });
    }

    @Test
    void testAddNegativeDigitThrowsException() {
        assertThrows(IllegalArgumentException.class, () -> {
            digitList.add(-5);
        });
    }

    /* ---------------- Remove Tests ---------------- */

    @Test
    void testRemoveFirstDigit() {
        digitList.remove(0);
        assertEquals(2345, digitList.intValue());
        assertEquals(4, digitList.size());
    }

    @Test
    void testRemoveMiddleDigit() {
        digitList.remove(2);
        assertEquals(1245, digitList.intValue());
    }

    @Test
    void testRemoveLastDigit() {
        digitList.remove(4);
        assertEquals(1234, digitList.intValue());
    }

    @Test
    void testRemoveFromSingleDigitResultsInZero() {
        DigitList dl = new DigitList(5);
        dl.remove(0);
        assertEquals(0, dl.intValue());
        assertEquals(1, dl.size());
    }

    @Test
    void testRemoveAllDigitsOneByOne() {
        DigitList dl = new DigitList(123);
        dl.remove(0); // 23
        assertEquals(23, dl.intValue());
        dl.remove(0); // 3
        assertEquals(3, dl.intValue());
        dl.remove(0); // 0
        assertEquals(0, dl.intValue());
    }

    @Test
    void testRemoveWithInvalidIndexThrowsException() {
        assertThrows(IndexOutOfBoundsException.class, () -> {
            digitList.remove(10);
        });
    }

    @Test
    void testRemoveWithNegativeIndexThrowsException() {
        assertThrows(IndexOutOfBoundsException.class, () -> {
            digitList.remove(-1);
        });
    }

    /* ---------------- Complex Operation Tests ---------------- */

    @Test
    void testMultipleOperationsSequence() {
        DigitList dl = new DigitList(100);
        dl.set(0, 2); // 200
        dl.add(5); // 2005
        dl.remove(2); // 205
        dl.set(1, 9); // 295

        assertEquals(295, dl.intValue());
    }

    @Test
    void testBuildNumberFromZero() {
        DigitList dl = new DigitList(0);
        dl.set(0, 1);
        dl.add(2);
        dl.add(3);
        dl.add(4);
        dl.add(5);

        assertEquals(12345, dl.intValue());
    }

    @Test
    void testReverseDigits() {
        DigitList dl = new DigitList(12345);
        // Swap digits to reverse
        int temp = dl.get(0);
        dl.set(0, dl.get(4));
        dl.set(4, temp);

        temp = dl.get(1);
        dl.set(1, dl.get(3));
        dl.set(3, temp);

        assertEquals(54321, dl.intValue());
    }

    /* ---------------- Edge Case Tests ---------------- */

    @Test
    void testLargeNumber() {
        DigitList dl = new DigitList(2147483647); // Max int value
        assertEquals(10, dl.size());
        assertEquals(2, dl.get(0));
        assertEquals(7, dl.get(9));
    }

    @Test
    void testAllZeros() {
        DigitList dl = new DigitList(0);
        dl.add(0);
        assertEquals(0, dl.intValue()); // Should be 00 -> 0
    }

    @Test
    void testAllNines() {
        DigitList dl = new DigitList(9999);
        assertEquals(4, dl.size());
        for (int i = 0; i < 4; i++) {
            assertEquals(9, dl.get(i));
        }
    }

    /* ---------------- ToString Tests ---------------- */

    @Test
    void testToString() {
        assertEquals("12345", digitList.toString());
    }

    @Test
    void testToStringWithZero() {
        DigitList dl = new DigitList(0);
        assertEquals("0", dl.toString());
    }

    @Test
    void testToStringAfterOperations() {
        digitList.add(6);
        digitList.remove(0);
        assertEquals("23456", digitList.toString());
    }

    /* ---------------- Boundary Tests ---------------- */

    @Test
    void testGetAllDigits() {
        int[] expected = { 1, 2, 3, 4, 5 };
        for (int i = 0; i < expected.length; i++) {
            assertEquals(expected[i], digitList.get(i));
        }
    }

    @Test
    void testSetAllDigits() {
        for (int i = 0; i < digitList.size(); i++) {
            digitList.set(i, 9);
        }
        assertEquals(99999, digitList.intValue());
    }

    @Test
    void testRemoveUntilZero() {
        DigitList dl = new DigitList(12);
        dl.remove(0); // 2
        dl.remove(0); // 0
        assertEquals(0, dl.intValue());
        assertEquals(1, dl.size());
    }
}
