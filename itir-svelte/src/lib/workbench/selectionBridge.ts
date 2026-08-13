import { writable, type Readable } from 'svelte/store';

export type SelectionBridgeReason = 'select' | 'hover' | 'clear' | 'sync' | 'scope';
export type SelectionBridgeScope = 'local' | 'expanded';

export type SelectionBridgeState<T> = {
  active: T | null;
  hovered: T | null;
  scope: SelectionBridgeScope;
  reason: SelectionBridgeReason | null;
  updatedAt: number;
};

export type SelectionBridge<T> = Readable<SelectionBridgeState<T>> & {
  setActive: (value: T | null, reason?: SelectionBridgeReason) => void;
  setHovered: (value: T | null, reason?: SelectionBridgeReason) => void;
  clear: () => void;
  setScope: (scope: SelectionBridgeScope) => void;
};

export function createSelectionBridge<T>(
  initialActive: T | null = null,
  initialScope: SelectionBridgeScope = 'local'
): SelectionBridge<T> {
  const now = Date.now();
  const store = writable<SelectionBridgeState<T>>({
    active: initialActive,
    hovered: null,
    scope: initialScope,
    reason: null,
    updatedAt: now
  });

  function update(
    patch: Partial<SelectionBridgeState<T>>,
    reason: SelectionBridgeReason
  ) {
    store.update((state) => ({
      ...state,
      ...patch,
      reason,
      updatedAt: Date.now()
    }));
  }

  return {
    subscribe: store.subscribe,
    setActive(value, reason = 'select') {
      update({ active: value }, reason);
    },
    setHovered(value, reason = 'hover') {
      update({ hovered: value }, reason);
    },
    clear() {
      update({ active: null, hovered: null }, 'clear');
    },
    setScope(scope) {
      update({ scope }, 'scope');
    }
  };
}

