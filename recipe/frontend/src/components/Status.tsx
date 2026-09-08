import type { ReactNode } from 'react';

type Props = { kind?: 'ok' | 'pending' | 'error'; children: ReactNode };

export function Status({ kind = 'pending', children }: Props) {
  return <span className={`status status-${kind}`}>{children}</span>;
}

export function Message({ children, kind = 'pending' }: Props) {
  return <div className={`message message-${kind}`}>{children}</div>;
}
