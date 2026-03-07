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
  tokenStart: number;
  tokenEnd: number;
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
  tokenCount: number;
  relationCount: number;
  promotedCount: number;
  tokens: TextDebugToken[];
  relations: TextDebugRelation[];
};

export type TextDebugPayload = {
  events: TextDebugEvent[];
  unavailableReason: string | null;
};
