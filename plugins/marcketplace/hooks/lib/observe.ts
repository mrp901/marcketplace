import type { StateDocSeen } from '../../types'
import { childKeys, entriesUnder, fenceBodies, topLevelKeys, utf8Bytes } from './yaml-lite.ts'

export type ProfileSeen = { fallbackChannelId: string; feedChannelIds: string[]; surfaceId?: string }

const FALLBACK = /^\s*fallback_channel_id:\s*["']?([A-Za-z0-9_-]+)/m

/** The candidate YAML in a text: its fenced blocks, or the text itself when it has none. */
const yamlIn = (text: string, marker: RegExp): string => {
  const fenced = fenceBodies(text).find((body) => marker.test(body))
  return fenced ?? text
}

/** The profile's notify channel, feed channels and surface, when the text holds a profile. */
export const scanProfile = (text: string): ProfileSeen | undefined => {
  if (!text.includes('fallback_channel_id:')) return undefined
  const yaml = yamlIn(text, FALLBACK)
  const fallback = FALLBACK.exec(yaml)?.[1]
  if (!fallback) return undefined
  const feedChannelIds = entriesUnder(yaml, 'tracker_feed_channels')
    .map((e) => e.value)
    .filter((v) => /^[A-Za-z0-9_-]+$/.test(v))
  const surfaceId = entriesUnder(yaml, 'surface', true).find((e) => e.key === 'id')?.value
  return surfaceId
    ? { fallbackChannelId: fallback, feedChannelIds, surfaceId }
    : { fallbackChannelId: fallback, feedChannelIds }
}

// Not anchored to a line start: in storage format the first key follows `<![CDATA[`.
const STATE_MARK = /\b(state_version|shard_version):/

/** Size, top-level keys and `runs` children of a state or shard document in the text. */
export const scanStateDoc = (text: string): StateDocSeen | undefined => {
  if (!STATE_MARK.test(text)) return undefined
  const yaml = yamlIn(text, STATE_MARK)
  return { bytes: utf8Bytes(yaml), topKeys: topLevelKeys(yaml), runsKeys: childKeys(yaml, 'runs') }
}

const NOT_A_DOCUMENT = /^(cloud|site|tenant|workspace|space|team|agent|tool_use|parent|request|session)_?id$/i
const DOCUMENT_ARG = /(id|path)$/i

/** The values of a call's arguments that name a document: `pageId`, `path`, `fileId` and the like. */
export const idArgs = (input: unknown): string[] => {
  if (input === null || typeof input !== 'object') return []
  const ids: string[] = []
  for (const [key, value] of Object.entries(input as Record<string, unknown>)) {
    if (!DOCUMENT_ARG.test(key) || NOT_A_DOCUMENT.test(key)) continue
    if (typeof value !== 'string' && typeof value !== 'number') continue
    const id = String(value)
    if (id && !ids.includes(id)) ids.push(id)
  }
  return ids
}
