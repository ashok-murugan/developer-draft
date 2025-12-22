export interface DiagnosticResponse {
    summary: string;
    rootCause: string;
    diagnosticSteps: string[];
    suggestedFix: string;
    confidence: number;
}

export interface ExplainTextRequest {
    content: string;
    context?: string;
}

export interface ExplainImageRequest {
    imageBase64: string;
    context?: string;
}

export interface ErrorResponse {
    errorCode: string;
    message: string;
}
