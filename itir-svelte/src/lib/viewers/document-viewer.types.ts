export type DocumentHighlightKind = 'active' | 'relation_peer' | 'echo';
export type DocumentHighlightSource = 'mention' | 'receipt' | 'label_fallback' | 'event_span';
export type DocumentLineSelectEvent = {
  lineNumber: number;
  text: string;
  charStart: number;
  charEnd: number;
};
export type DocumentHighlight = {
  key: string;
  charStart: number;
  charEnd: number;
  color: string;
  opacity?: number;
  kind?: DocumentHighlightKind;
  label?: string;
  source?: DocumentHighlightSource;
  sourceArtifactId?: string;
};

export type DocumentViewerProps = {
  title?: string;
  text?: string;
  mode?: 'plain' | 'markdown';
  showSearch?: boolean;
  showLineNumbers?: boolean;
  maxHeightPx?: number;
  placeholder?: string;
  ariaLabel?: string | null;
  searchAriaLabel?: string;
  highlights?: DocumentHighlight[];
  selectedHighlightKey?: string | null;
};
