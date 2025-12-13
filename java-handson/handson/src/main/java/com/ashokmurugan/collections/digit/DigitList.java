package com.ashokmurugan.collections.digit;

/**
 * An ADT that treats an int as a mutable list of decimal digits.
 *
 * Rules:
 * - Only non-negative integers
 * - Digits are 0–9
 * - Indexing is zero-based, left to right
 * - Zero is represented as [0]
 * - Removing the last digit results in [0]
 */
public class DigitList {

    private int value;

    public DigitList(int value) {
        if (value < 0) {
            throw new IllegalArgumentException("Negative numbers not allowed");
        }
        this.value = value;
    }

    /* ---------------- Basic helpers ---------------- */

    public int intValue() {
        return value;
    }

    public int size() {
        if (value == 0) return 1;

        int n = value;
        int count = 0;
        while (n > 0) {
            count++;
            n /= 10;
        }
        return count;
    }

    private int pow10(int exp) {
        int r = 1;
        for (int i = 0; i < exp; i++) {
            r *= 10;
        }
        return r;
    }

    private void checkIndex(int index) {
        if (index < 0 || index >= size()) {
            throw new IndexOutOfBoundsException(
                    "Index: " + index + ", Size: " + size()
            );
        }
    }

    private void checkDigit(int digit) {
        if (digit < 0 || digit > 9) {
            throw new IllegalArgumentException("Digit must be 0–9");
        }
    }

    /* ---------------- Operations ---------------- */

    /** Returns the digit at index */
    public int get(int index) {
        checkIndex(index);
        int len = size();
        int divisor = pow10(len - index - 1);
        return (value / divisor) % 10;
    }

    /** Replaces the digit at index */
    public void set(int index, int digit) {
        checkIndex(index);
        checkDigit(digit);

        int len = size();
        int divisor = pow10(len - index - 1);
        int oldDigit = (value / divisor) % 10;

        value = value - oldDigit * divisor + digit * divisor;
    }

    /** Appends a digit at the end */
    public void add(int digit) {
        checkDigit(digit);
        value = value * 10 + digit;
    }

    /** Removes the digit at index */
    public void remove(int index) {
        checkIndex(index);

        int len = size();
        if (len == 1) {
            value = 0;
            return;
        }

        int divisor = pow10(len - index - 1);
        int left = value / (divisor * 10);
        int right = value % divisor;

        value = left * divisor + right;
    }

    @Override
    public String toString() {
        return String.valueOf(value);
    }
}
