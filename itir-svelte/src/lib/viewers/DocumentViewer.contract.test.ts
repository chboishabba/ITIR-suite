import type { DocumentViewerProps } from './document-viewer.types';

// Lightweight type contract regression: keep prop surface stable for search accessibility.
type Expect<Cond extends true> = Cond;

// Should expose a configurable search aria label string.
type _searchAriaLabelExists = Expect<'searchAriaLabel' extends keyof DocumentViewerProps ? true : false>;
type _searchAriaLabelIsString = Expect<DocumentViewerProps['searchAriaLabel'] extends string | undefined ? true : false>;
