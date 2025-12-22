import { DiagnosticResponse, ExplainTextRequest, ExplainImageRequest } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';

class ApiService {
    private async fetchApi<T>(endpoint: string, options: RequestInit): Promise<T> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'API request failed');
        }

        return response.json();
    }

    async explainText(request: ExplainTextRequest): Promise<DiagnosticResponse> {
        return this.fetchApi<DiagnosticResponse>('/api/explain/text', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async explainImage(request: ExplainImageRequest): Promise<DiagnosticResponse> {
        return this.fetchApi<DiagnosticResponse>('/api/explain/image', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    }

    async healthCheck(): Promise<string> {
        const response = await fetch(`${API_BASE_URL}/api/explain/health`);
        return response.text();
    }
}

export const apiService = new ApiService();
