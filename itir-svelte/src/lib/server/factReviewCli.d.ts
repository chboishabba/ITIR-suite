export function parseFactReviewCliPayload<T>(raw: string, field: string): T;

export function classifyFactReviewErrorMessage(message: string | null | undefined): {
  kind: 'missing_run' | 'parse_error' | 'backend_error' | 'unknown_error';
  title: string;
  detail: string;
};
