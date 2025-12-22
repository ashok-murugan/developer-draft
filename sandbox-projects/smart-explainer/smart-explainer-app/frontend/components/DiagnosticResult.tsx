import { DiagnosticResponse } from '@/types/api';

interface DiagnosticResultProps {
    result: DiagnosticResponse;
}

export default function DiagnosticResult({ result }: DiagnosticResultProps) {
    const confidencePercent = Math.round(result.confidence * 100);
    const confidenceColor =
        result.confidence >= 0.8 ? 'text-green-600' :
            result.confidence >= 0.6 ? 'text-yellow-600' :
                'text-orange-600';

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6 animate-fade-in">
            {/* Summary Card */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-lg">
                <h3 className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">
                    Summary
                </h3>
                <p className="text-lg text-gray-800 font-medium">{result.summary}</p>
            </div>

            {/* Root Cause */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-md">
                <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-3">
                    🔍 Root Cause
                </h3>
                <p className="text-gray-700 leading-relaxed">{result.rootCause}</p>
            </div>

            {/* Diagnostic Steps */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-md">
                <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
                    📋 Diagnostic Steps
                </h3>
                <ol className="space-y-3">
                    {result.diagnosticSteps.map((step, index) => (
                        <li key={index} className="flex items-start gap-3">
                            <span className="flex-shrink-0 w-6 h-6 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-sm font-semibold">
                                {index + 1}
                            </span>
                            <span className="text-gray-700 pt-0.5">{step}</span>
                        </li>
                    ))}
                </ol>
            </div>

            {/* Suggested Fix */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-xl p-6 shadow-lg">
                <h3 className="text-sm font-semibold text-green-700 uppercase tracking-wide mb-3">
                    ✅ Suggested Fix
                </h3>
                <p className="text-gray-800 leading-relaxed">{result.suggestedFix}</p>
            </div>

            {/* Confidence Score */}
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-md">
                <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
                        Confidence Score
                    </h3>
                    <span className={`text-2xl font-bold ${confidenceColor}`}>
                        {confidencePercent}%
                    </span>
                </div>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-indigo-500 to-blue-500 transition-all duration-500"
                        style={{ width: `${confidencePercent}%` }}
                    />
                </div>
            </div>
        </div>
    );
}
