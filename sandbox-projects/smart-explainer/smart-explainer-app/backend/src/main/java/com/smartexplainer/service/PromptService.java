package com.smartexplainer.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * Service for loading and managing prompt templates.
 * Prompts are treated as versioned business logic.
 */
@Slf4j
@Service
public class PromptService {

    private static final String DIAGNOSTIC_PROMPT_PATH = "prompts/diagnostic-prompt.txt";

    private String diagnosticPromptTemplate;

    public PromptService() {
        loadPrompts();
    }

    /**
     * Build diagnostic prompt with content and context
     */
    public String buildDiagnosticPrompt(String content, String context) {
        String contextValue = (context != null && !context.isBlank()) ? context : "general";

        return diagnosticPromptTemplate
                .replace("{INPUT_CONTENT}", content)
                .replace("{CONTEXT}", contextValue);
    }

    private void loadPrompts() {
        try {
            ClassPathResource resource = new ClassPathResource(DIAGNOSTIC_PROMPT_PATH);
            diagnosticPromptTemplate = new String(
                    resource.getInputStream().readAllBytes(),
                    StandardCharsets.UTF_8);
            log.info("Loaded diagnostic prompt template");
        } catch (IOException e) {
            log.error("Failed to load prompt template", e);
            throw new RuntimeException("Failed to load prompt template", e);
        }
    }
}
