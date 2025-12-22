package com.smartexplainer.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Structured diagnostic response returned by the API.
 * This is the core output contract for Smart Explainer.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DiagnosticResponse {

    /**
     * Brief summary of the issue
     */
    private String summary;

    /**
     * Root cause analysis
     */
    private String rootCause;

    /**
     * Ordered list of diagnostic steps to investigate
     */
    private List<String> diagnosticSteps;

    /**
     * Suggested fix or remediation
     */
    private String suggestedFix;

    /**
     * Confidence score (0.0 to 1.0)
     */
    private Double confidence;
}
