package com.smartexplainer.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.smartexplainer.config.GeminiConfig;
import com.smartexplainer.exception.GeminiClientException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Isolated client for Gemini API interactions.
 * All Gemini calls flow through this component.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class GeminiClient {

    private final WebClient geminiWebClient;
    private final GeminiConfig geminiConfig;
    private final ObjectMapper objectMapper;

    private static final String MODEL = "gemini-2.0-flash-exp";

    /**
     * Generate content from text prompt
     */
    public String generateContent(String prompt) {
        log.info("Calling Gemini API with text prompt");

        Map<String, Object> requestBody = buildTextRequest(prompt);

        return callGeminiApi(requestBody);
    }

    /**
     * Generate content from text prompt with image
     */
    public String generateContentWithImage(String prompt, String base64Image) {
        log.info("Calling Gemini API with text and image");

        Map<String, Object> requestBody = buildMultimodalRequest(prompt, base64Image);

        return callGeminiApi(requestBody);
    }

    private String callGeminiApi(Map<String, Object> requestBody) {
        try {
            String response = geminiWebClient
                    .post()
                    .uri("/v1beta/models/" + MODEL + ":generateContent?key=" + geminiConfig.getApiKey())
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(geminiConfig.getTimeoutSeconds()))
                    .block();

            return extractTextFromResponse(response);

        } catch (Exception e) {
            log.error("Gemini API call failed", e);
            throw new GeminiClientException("Failed to call Gemini API: " + e.getMessage(), e);
        }
    }

    private Map<String, Object> buildTextRequest(String prompt) {
        Map<String, Object> textPart = Map.of("text", prompt);
        Map<String, Object> content = Map.of("parts", List.of(textPart));

        return Map.of(
                "contents", List.of(content),
                "generationConfig", Map.of(
                        "temperature", 0.2,
                        "topK", 40,
                        "topP", 0.95,
                        "maxOutputTokens", 2048));
    }

    private Map<String, Object> buildMultimodalRequest(String prompt, String base64Image) {
        Map<String, Object> textPart = Map.of("text", prompt);
        Map<String, Object> imagePart = Map.of(
                "inlineData", Map.of(
                        "mimeType", "image/png",
                        "data", base64Image));

        Map<String, Object> content = Map.of("parts", List.of(textPart, imagePart));

        return Map.of(
                "contents", List.of(content),
                "generationConfig", Map.of(
                        "temperature", 0.2,
                        "topK", 40,
                        "topP", 0.95,
                        "maxOutputTokens", 2048));
    }

    private String extractTextFromResponse(String response) {
        try {
            JsonNode root = objectMapper.readTree(response);
            JsonNode candidates = root.path("candidates");

            if (candidates.isEmpty()) {
                throw new GeminiClientException("No candidates in Gemini response");
            }

            JsonNode content = candidates.get(0).path("content");
            JsonNode parts = content.path("parts");

            if (parts.isEmpty()) {
                throw new GeminiClientException("No parts in Gemini response");
            }

            return parts.get(0).path("text").asText();

        } catch (Exception e) {
            log.error("Failed to parse Gemini response", e);
            throw new GeminiClientException("Failed to parse Gemini response: " + e.getMessage(), e);
        }
    }
}
