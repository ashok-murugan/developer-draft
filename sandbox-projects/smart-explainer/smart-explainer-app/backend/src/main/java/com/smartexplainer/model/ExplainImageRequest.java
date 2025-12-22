package com.smartexplainer.model;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Request to explain image-based technical content (screenshots, terminal
 * output, etc.)
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExplainImageRequest {

    /**
     * Base64-encoded image data
     */
    @NotBlank(message = "Image data cannot be empty")
    private String imageBase64;

    /**
     * Optional context hint (e.g., "terminal-error", "ui-bug")
     */
    private String context;
}
