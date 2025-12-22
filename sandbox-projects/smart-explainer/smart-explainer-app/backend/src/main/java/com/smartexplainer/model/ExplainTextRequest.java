package com.smartexplainer.model;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request to explain text-based technical content
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExplainTextRequest {

    /**
     * The technical content to analyze (error, log, stack trace, etc.)
     */
    @NotBlank(message = "Content cannot be empty")
    private String content;

    /**
     * Optional context hint (e.g., "java", "python", "terminal")
     */
    private String context;
}
