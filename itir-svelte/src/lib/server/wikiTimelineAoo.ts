export type {
  AooActor,
  AooObject,
  AooCitation,
  AooSlReference,
  AooNegation,
  AooTimelineFact,
  AooPropositionArgument,
  AooProposition,
  AooPropositionLink,
  SpanCandidate,
  AooEvent,
  WikiTimelineAooPayload,
} from './wiki_timeline/types';

export { loadWikiTimelineAoo, loadWikiTimelineAooSource } from './wiki_timeline/aoo_adapter';
