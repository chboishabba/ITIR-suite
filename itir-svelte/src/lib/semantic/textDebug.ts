export type TextDebugAnchorSource = 'mention' | 'receipt' | 'label_fallback';

export type TextDebugAnchorRole = 'subject' | 'predicate' | 'object';

export type TextDebugToken = {
  index: number;
  text: string;
  start: number;
  end: number;
};

export type TextDebugAnchor = {
  key: string;
  role: TextDebugAnchorRole;
  label: string;
  source: TextDebugAnchorSource;
  charStart: number;
  charEnd: number;
  tokenStart: number;
  tokenEnd: number;
  sourceArtifactId: string;
};

export type TextDebugRelation = {
  relationId: string;
  predicateKey: string;
  displayLabel: string;
  promotionStatus: string;
  confidenceTier: string;
  family: string;
  color: string;
  opacity: number;
  anchors: TextDebugAnchor[];
};

export type TextDebugEvent = {
  eventId: string;
  text: string;
  sourceId?: string | null;
  sourceType?: string | null;
  sourceDocumentId?: string | null;
  sourceCharStart?: number | null;
  sourceCharEnd?: number | null;
  tokenCount: number;
  relationCount: number;
  promotedCount: number;
  tokens: TextDebugToken[];
  relations: TextDebugRelation[];
};

export type TextDebugSourceDocument = {
  sourceDocumentId: string;
  sourceType: string;
  title: string;
  text: string;
  eventCount: number;
  eventIds: string[];
};

export type TextDebugPayload = {
  events: TextDebugEvent[];
  unavailableReason: string | null;
};
