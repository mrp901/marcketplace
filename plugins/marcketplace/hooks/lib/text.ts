/** Default cap on how much text the observer reads from one call, in characters. */
export const TEXT_CAP = 300_000

/** Every string inside a value, depth first, until `cap` characters are collected. */
export const stringValues = (value: unknown, cap = TEXT_CAP): string[] => {
  const out: string[] = []
  let total = 0
  const walk = (v: unknown, depth: number): void => {
    if (total >= cap || depth > 8) return
    if (typeof v === 'string') {
      const piece = v.slice(0, cap - total)
      out.push(piece)
      total += piece.length
    } else if (Array.isArray(v)) {
      for (const item of v) walk(item, depth + 1)
    } else if (v !== null && typeof v === 'object') {
      for (const item of Object.values(v as Record<string, unknown>)) walk(item, depth + 1)
    }
  }
  walk(value, 0)
  return out
}

/** The text a tool call answered: core's own `text` when it has one, else the strings in `result`. */
export const resultText = (answer: unknown, cap = TEXT_CAP): string => {
  if (answer === null || typeof answer !== 'object') return ''
  const { text, result } = answer as { text?: unknown; result?: unknown }
  if (typeof text === 'string' && text.length > 0) return text.slice(0, cap)
  return stringValues(result, cap).join('\n')
}
