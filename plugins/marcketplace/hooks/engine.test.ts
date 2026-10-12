// The observer through the engine: the plugin's hooks run above the test's own,
// which stand for the engine beneath. State is read back by hooking state.set,
// since a test's $ has no reader for another plugin's state.

import { describe, expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'
import { DISPATCH, PROFILE_PAGE, STATE_PAGE } from './test-fixtures.ts'

type Write = { key: string; id?: string; value: unknown }

const recordWrites = (on: On): Write[] => {
  const writes: Write[] = []
  on('state.set', { plugin: 'marcketplace' }, ($, e, next) => {
    writes.push({ key: e.key, ...(e.id === undefined ? {} : { id: e.id }), value: e.value })
    return next(e)
  })
  return writes
}

const lastOf = (writes: Write[], key: string): unknown => writes.filter((w) => w.key === key).at(-1)?.value

const notices = (rows: readonly { message: { type: string; content: unknown } }[]): string[] =>
  rows
    .filter((r) => r.message.type === 'system')
    .map((r) => JSON.stringify(r.message.content))

const ROUTINE = 'Run /marcketplace:briefing profile=confluence:x/889000111 unattended'
const GET_PAGE = 'mcp__confluence__getConfluencePage'
const UPDATE_PAGE = 'mcp__confluence__updateConfluencePage'

describe('observer', () => {
  test('a routine prompt records the run and announces once', async ($, on) => {
    mock.env(on, { MARCKETPLACE_GUARDS: 'on' })
    const session = mock.session(on)
    const writes = recordWrites(on)
    on('prompt.submit', ($, e) => ({ text: e.text }))

    await $.prompt.submit({ text: ROUTINE, wait: false } as never)
    await $.prompt.submit({ text: 'Run /marcketplace:briefing again', wait: false } as never)

    expect(writes.find((w) => w.key === 'main')?.value).toEqual({
      unattended: true,
      skill: 'briefing',
      profileRef: 'confluence:x/889000111',
    })
    const lines = notices(session.appended())
    expect(lines).toHaveLength(1)
    expect(lines[0]).toContain('loaded · mode on · unattended run of briefing')
  })

  test('a profile read teaches the channel ids and leaves the answer alone', async ($, on) => {
    const session = mock.session(on)
    const writes = recordWrites(on)
    const answer = { result: { content: [{ type: 'text', text: PROFILE_PAGE }] } }
    on('tool.call', { tool: GET_PAGE }, () => answer)

    const got = await $.tool.call({ tool: GET_PAGE, pageId: '889000111', cloudId: 'example-cloud' } as never)

    expect(got).toEqual(answer)
    expect(lastOf(writes, 'learned')).toEqual({
      feedChannelIds: ['CEXAMPLEFEED01', 'CEXAMPLEFEED02'],
      stateDocs: {},
      fallbackChannelId: 'CEXAMPLEHOME01',
      surfaceId: 'FEXAMPLECANVAS1',
    })
    const lines = notices(session.appended())
    expect(lines).toHaveLength(1)
    expect(lines[0]).toContain('profile seen · home channel CEXAMPLEHOME01 · 2 feed channels · surface FEXAMPLECANVAS1')
  })

  test('a state write is recorded under its page id', async ($, on) => {
    const session = mock.session(on)
    const writes = recordWrites(on)
    on('tool.call', { tool: UPDATE_PAGE }, () => ({ result: 'ok' }))

    await $.tool.call({ tool: UPDATE_PAGE, pageId: '990111222', body: STATE_PAGE } as never)

    const learned = lastOf(writes, 'learned') as { stateDocs: Record<string, { topKeys: string[]; runsKeys: string[] }> }
    expect(learned.stateDocs['990111222']?.runsKeys).toEqual(['briefing', 'proactive-router'])
    expect(notices(session.appended())[0]).toContain('state document seen · 990111222')
  })

  test('a hub dispatch is recorded as a handler', async ($, on) => {
    const session = mock.session(on)
    const writes = recordWrites(on)
    on('agent.spawn', () => ({ model: 'sonnet', agentId: 'agent-1' }))

    const got = await $.agent.spawn({
      tool_use_id: 'toolu_dispatch',
      prompt: DISPATCH,
      description: 'dispatch a sweep line',
      subagentType: 'general-purpose',
      provider: { plugin: 'engine', tier: 'core' },
      parentModel: 'sonnet',
      background: false,
      fork: false,
    } as never)

    expect(got).toEqual({ model: 'sonnet', agentId: 'agent-1' })
    const agent = writes.find((w) => w.key === 'agents' && w.id === 'agent-1')
    expect(agent?.value).toEqual({
      kind: 'handler',
      mode: 'targeted',
      unattended: true,
      handler: 'action-sweep',
      budgetToolCalls: 25,
    })
    expect(notices(session.appended())[0]).toContain('handler dispatch · action-sweep · mode targeted · budget 25 calls')
  })

  test('with the switch off nothing is observed', async ($, on) => {
    mock.env(on, { MARCKETPLACE_GUARDS: 'off' })
    const session = mock.session(on)
    const writes = recordWrites(on)
    on('tool.call', { tool: GET_PAGE }, () => ({ result: PROFILE_PAGE }))

    await $.tool.call({ tool: GET_PAGE, pageId: '889000111' } as never)

    expect(writes.filter((w) => w.key === 'learned')).toHaveLength(0)
    expect(notices(session.appended())).toHaveLength(0)
  })

  test('nothing is refused in this release', async ($, on) => {
    on('tool.call', { tool: 'Bash' }, () => ({ result: 'ran' }))
    expect(await $.tool.call({ tool: 'Bash', command: 'twg login' })).toEqual({ result: 'ran' })
  })
})
