export type Unsubscriber = () => void;
export type Subscriber<T> = (value: T) => void;

export type WritableStore<T> = {
  subscribe: (run: Subscriber<T>) => Unsubscriber;
  set: (value: T) => void;
  update: (fn: (value: T) => T) => void;
};

// Minimal Svelte-store-compatible writable implementation.
// This avoids importing `svelte/store` in modules that may be evaluated during SSR.
export function writable<T>(initial: T): WritableStore<T> {
  let value = initial;
  const subs = new Set<Subscriber<T>>();

  function set(next: T) {
    value = next;
    for (const fn of subs) fn(value);
  }

  function update(fn: (value: T) => T) {
    set(fn(value));
  }

  function subscribe(run: Subscriber<T>): Unsubscriber {
    subs.add(run);
    run(value);
    return () => subs.delete(run);
  }

  return { subscribe, set, update };
}

