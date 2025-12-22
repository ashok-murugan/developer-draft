package com.smartexplainer.exception;

/**
 * Exception thrown when Gemini API interaction fails
 */
public class GeminiClientException extends RuntimeException {

    public GeminiClientException(String message) {
        super(message);
    }

    public GeminiClientException(String message, Throwable cause) {
        super(message, cause);
    }
}
