import type { GuardMode } from '../../types'

/** The kill switch a routine environment sets: off, warn, on (the default) or strict. */
export const MODE_ENV = 'MARCKETPLACE_GUARDS'

const MODES: readonly GuardMode[] = ['off', 'warn', 'on', 'strict']

export const parseMode = (raw: string | undefined): GuardMode => {
  const value = (raw ?? '').trim().toLowerCase()
  return (MODES as readonly string[]).includes(value) ? (value as GuardMode) : 'on'
}

/** The version field of plugin.json, or `unknown` when it cannot be read. */
export const parseVersion = (manifest: string): string => {
  try {
    const version = (JSON.parse(manifest) as { version?: unknown }).version
    return typeof version === 'string' && version ? version : 'unknown'
  } catch {
    return 'unknown'
  }
}
