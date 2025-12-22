package com.smartexplainer.api;

import com.smartexplainer.model.DiagnosticResponse;
import com.smartexplainer.model.ExplainImageRequest;
import com.smartexplainer.model.ExplainTextRequest;
import com.smartexplainer.service.DiagnosticService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST API controller for diagnostic explanations.
 * This is the public API surface of Smart Explainer.
 */
@Slf4j
@RestController
@RequestMapping("/api/explain")
@RequiredArgsConstructor
public class ExplainController {

    private final DiagnosticService diagnosticService;

    /**
     * Explain text-based technical content
     * 
     * POST /api/explain/text
     */
    @PostMapping("/text")
    public ResponseEntity<DiagnosticResponse> explainText(
            @Valid @RequestBody ExplainTextRequest request) {
        log.info("Received text explanation request with context: {}", request.getContext());

        DiagnosticResponse response = diagnosticService.explainText(
                request.getContent(),
                request.getContext());

        return ResponseEntity.ok(response);
    }

    /**
     * Explain image-based technical content
     * 
     * POST /api/explain/image
     */
    @PostMapping("/image")
    public ResponseEntity<DiagnosticResponse> explainImage(
            @Valid @RequestBody ExplainImageRequest request) {
        log.info("Received image explanation request with context: {}", request.getContext());

        DiagnosticResponse response = diagnosticService.explainImage(
                request.getImageBase64(),
                request.getContext());

        return ResponseEntity.ok(response);
    }

    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Smart Explainer API is running");
    }
}
