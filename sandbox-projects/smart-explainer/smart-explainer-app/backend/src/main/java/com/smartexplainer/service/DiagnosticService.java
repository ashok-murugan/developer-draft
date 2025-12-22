package com.smartexplainer.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartexplainer.ai.GeminiClient;
import com.smartexplainer.exception.GeminiClientException;
import com.smartexplainer.model.DiagnosticResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Core service orchestrating diagnostic explanations.
 * This service coordinates prompts and Gemini calls.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class DiagnosticService {

    private final GeminiClient geminiClient;
    private final PromptService promptService;
    private final ObjectMapper objectMapper;

    /**
     * Explain text-based technical content
     */
    public DiagnosticResponse explainText(String content, String context) {
        log.info("Explaining text content with context: {}", context);

        // Build prompt from template
        String prompt = promptService.buildDiagnosticPrompt(content, context);

        // Call Gemini
        String geminiResponse = geminiClient.generateContent(prompt);

        // Parse and validate response
        return parseAndValidateResponse(geminiResponse);
    }

    /**
     * Explain image-based technical content
     */
    public DiagnosticResponse explainImage(String base64Image, String context) {
        log.info("Explaining image content with context: {}", context);

        // Build prompt from template
        String prompt = promptService.buildDiagnosticPrompt(
                "Analyze this screenshot or terminal output image.",
                context);

        // Call Gemini with multimodal input
        String geminiResponse = geminiClient.generateContentWithImage(prompt, base64Image);

        // Parse and validate response
        return parseAndValidateResponse(geminiResponse);
    }

    /**
     * Parse Gemini's JSON response and validate against schema
     */
    private DiagnosticResponse parseAndValidateResponse(String geminiResponse) {
        try {
            // Clean response (remove markdown code blocks if present)
            String cleanedResponse = geminiResponse.trim();
            if (cleanedResponse.startsWith("```json")) {
                cleanedResponse = cleanedResponse
                        .replaceFirst("```json\\s*", "")
                        .replaceFirst("```\\s*$", "")
                        .trim();
            } else if (cleanedResponse.startsWith("```")) {
                cleanedResponse = cleanedResponse
                        .replaceFirst("```\\s*", "")
                        .replaceFirst("```\\s*$", "")
                        .trim();
            }

            // Parse JSON
            DiagnosticResponse response = objectMapper.readValue(
                    cleanedResponse,
                    DiagnosticResponse.class);

            // Validate required fields
            validateResponse(response);

            log.info("Successfully parsed diagnostic response with confidence: {}",
                    response.getConfidence());

            return response;

        } catch (Exception e) {
            log.error("Failed to parse Gemini response: {}", geminiResponse, e);
            throw new GeminiClientException(
                    "Failed to parse structured response from Gemini: " + e.getMessage(),
                    e);
        }
    }

    private void validateResponse(DiagnosticResponse response) {
        if (response.getSummary() == null || response.getSummary().isBlank()) {
            throw new GeminiClientException("Response missing required field: summary");
        }
        if (response.getRootCause() == null || response.getRootCause().isBlank()) {
            throw new GeminiClientException("Response missing required field: rootCause");
        }
        if (response.getDiagnosticSteps() == null || response.getDiagnosticSteps().isEmpty()) {
            throw new GeminiClientException("Response missing required field: diagnosticSteps");
        }
        if (response.getSuggestedFix() == null || response.getSuggestedFix().isBlank()) {
            throw new GeminiClientException("Response missing required field: suggestedFix");
        }
        if (response.getConfidence() == null || response.getConfidence() < 0 || response.getConfidence() > 1) {
            throw new GeminiClientException("Response has invalid confidence value");
        }
    }
}
