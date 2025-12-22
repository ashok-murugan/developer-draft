package com.smartexplainer.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Error response for API failures
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ErrorResponse {

    /**
     * Error code (e.g., INVALID_INPUT, GEMINI_ERROR)
     */
    private String errorCode;

    /**
     * Human-readable error message
     */
    private String message;
}
