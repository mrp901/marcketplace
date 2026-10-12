// Just enough YAML reading for the profile and state documents: fenced blocks,
// top-level keys and the entries directly under one key. No YAML library is
// available to a hooks module, and none is needed for these checks.

const FENCE = /```ya?ml[^\n]*\n([\s\S]*?)```/g
const CDATA = /<!\[CDATA\[([\s\S]*?)\]\]>/g

/** The bodies of fenced YAML blocks, and of storage-format CDATA sections. */
export const fenceBodies = (text: string): string[] => {
  const bodies: string[] = []
  for (const m of text.matchAll(FENCE)) bodies.push(m[1] ?? '')
  for (const m of text.matchAll(CDATA)) bodies.push(m[1] ?? '')
  return bodies
}

/** Size in bytes as a connector stores it (UTF-8), not in characters. */
export const utf8Bytes = (s: string): number => new TextEncoder().encode(s).length

const indentOf = (line: string): number => line.length - line.trimStart().length

const isContent = (line: string): boolean => {
  const t = line.trim()
  return t.length > 0 && !t.startsWith('#')
}

const KEY = /^\s*([A-Za-z_][\w.-]*)\s*:(.*)$/

/** Keys at column zero, in order, each once. */
export const topLevelKeys = (yaml: string): string[] => {
  const keys: string[] = []
  for (const line of yaml.split('\n')) {
    if (!isContent(line) || indentOf(line) !== 0) continue
    const m = KEY.exec(line)
    if (m?.[1] && !keys.includes(m[1])) keys.push(m[1])
  }
  return keys
}

export type Entry = { key: string; value: string }

const scalar = (raw: string): string =>
  raw.replace(/\s+#.*$/, '').trim().replace(/^["']|["']$/g, '')

/**
 * The entries directly under the first line `key:` (at column zero when
 * `topOnly`), with their scalar values (empty for a nested block).
 */
export const entriesUnder = (yaml: string, key: string, topOnly = false): Entry[] => {
  const lines = yaml.split('\n')
  const start = lines.findIndex((line) => {
    if (!isContent(line) || (topOnly && indentOf(line) !== 0)) return false
    return KEY.exec(line)?.[1] === key
  })
  if (start < 0) return []
  const parentIndent = indentOf(lines[start] ?? '')
  const entries: Entry[] = []
  let childIndent = -1
  for (const line of lines.slice(start + 1)) {
    if (!isContent(line)) continue
    const indent = indentOf(line)
    if (indent <= parentIndent) break
    if (childIndent < 0) childIndent = indent
    if (indent !== childIndent) continue
    const m = KEY.exec(line)
    if (m?.[1]) entries.push({ key: m[1], value: scalar(m[2] ?? '') })
  }
  return entries
}

/** The keys directly under a top-level key, such as the skills under `runs`. */
export const childKeys = (yaml: string, key: string): string[] =>
  entriesUnder(yaml, key, true).map((e) => e.key)
