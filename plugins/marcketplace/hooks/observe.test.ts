import { describe, expect, test } from 'claude-code/testing'
import { idArgs, scanProfile, scanStateDoc } from './lib/observe.ts'
import { resultText } from './lib/text.ts'
import { PROFILE_PAGE, PROFILE_YAML, STATE_PAGE, STATE_YAML } from './test-fixtures.ts'

describe('scanProfile', () => {
  test('reads the channel and surface ids from a profile page', async () => {
    expect(scanProfile(PROFILE_PAGE)).toEqual({
      fallbackChannelId: 'CEXAMPLEHOME01',
      feedChannelIds: ['CEXAMPLEFEED01', 'CEXAMPLEFEED02'],
      surfaceId: 'FEXAMPLECANVAS1',
    })
  })
  test('reads a bare YAML body too', async () => {
    expect(scanProfile(PROFILE_YAML)?.fallbackChannelId).toBe('CEXAMPLEHOME01')
  })
  test('finds nothing in unrelated text', async () => {
    expect(scanProfile('notify mode is webhook')).toBeUndefined()
  })
})

describe('scanStateDoc', () => {
  test('reads size, top-level keys and runs from a state page', async () => {
    const seen = scanStateDoc(STATE_PAGE)
    expect(seen?.topKeys).toEqual(['state_version', 'installed_version', 'profile_ref', 'shards', 'runs', 'glossary', 'items'])
    expect(seen?.runsKeys).toEqual(['briefing', 'proactive-router'])
    expect(seen?.bytes).toBe(new TextEncoder().encode(`${STATE_YAML}\n`).length)
  })
  test('counts bytes, not characters', async () => {
    const seen = scanStateDoc(STATE_PAGE)
    expect(seen?.bytes).toBeGreaterThan(STATE_YAML.length)
  })
  test('reads a storage-format body the same way', async () => {
    const storage = `<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[${STATE_YAML}\n]]></ac:plain-text-body></ac:structured-macro>`
    expect(scanStateDoc(storage)).toEqual(scanStateDoc(STATE_PAGE))
  })
  test('ignores a profile', async () => {
    expect(scanStateDoc(PROFILE_PAGE)).toBeUndefined()
  })
})

describe('idArgs', () => {
  test('keeps document ids and drops site ids', async () => {
    expect(idArgs({ pageId: '990111222', cloudId: 'example-cloud' })).toEqual(['990111222'])
    expect(idArgs({ path: 'Shared/state.md', content: 'x' })).toEqual(['Shared/state.md'])
    expect(idArgs({ page_id: 990111222 })).toEqual(['990111222'])
  })
  test('ignores calls with no document argument', async () => {
    expect(idArgs({ query: 'is:saved' })).toEqual([])
  })
})

describe('resultText', () => {
  test('prefers core text, then the strings in result', async () => {
    expect(resultText({ text: 'core', result: 'other' })).toBe('core')
    expect(resultText({ result: { content: [{ type: 'text', text: 'a' }, { type: 'text', text: 'b' }] } })).toBe('text\na\ntext\nb')
  })
})
