import { describe, expect, test } from 'claude-code/testing'
import { classifyDispatch, parseInvocation, skillOf } from './lib/context.ts'
import { parseMode, parseVersion } from './lib/config.ts'
import { DISPATCH, READER } from './test-fixtures.ts'

describe('parseInvocation', () => {
  test('reads a routine prompt', async () => {
    expect(parseInvocation('Run /marcketplace:briefing profile=confluence:x/889000111 unattended')).toEqual({
      skill: 'briefing',
      unattended: true,
      profileRef: 'confluence:x/889000111',
    })
  })
  test('without the token the run is attended', async () => {
    expect(parseInvocation('/marcketplace:kb-note capture this')).toEqual({ skill: 'kb-note', unattended: false })
  })
  test('ignores text that names no marcketplace skill', async () => {
    expect(parseInvocation('please run unattended')).toBeUndefined()
  })
  test('only the literal token counts', async () => {
    expect(parseInvocation('/marcketplace:briefing an unattended-ish run')?.unattended).toBe(false)
    expect(parseInvocation('/marcketplace:briefing semiunattended')?.unattended).toBe(false)
  })
})

describe('classifyDispatch', () => {
  test('the hub payload is a handler dispatch', async () => {
    expect(classifyDispatch(DISPATCH, false)).toEqual({
      kind: 'handler',
      mode: 'targeted',
      unattended: true,
      handler: 'action-sweep',
      budgetToolCalls: 25,
    })
  })
  test('a thread reader under an unattended run is a reader', async () => {
    expect(classifyDispatch(READER, true)).toEqual({ kind: 'reader', unattended: true })
  })
  test('a mode line without the token is not a dispatch', async () => {
    const attended = DISPATCH.split('\n').filter((l) => l !== 'unattended').join('\n')
    expect(classifyDispatch(attended, false)).toEqual({ kind: 'other', unattended: false })
  })
})

describe('skillOf', () => {
  test('reads a Skill call for one of this plugin skills', async () => {
    expect(skillOf({ skill: 'marcketplace:reply-draft', args: 'profile=x unattended' })).toEqual({
      skill: 'reply-draft',
      unattended: true,
      profileRef: 'x',
    })
  })
  test('ignores another plugin skill', async () => {
    expect(skillOf({ skill: 'commit' })).toBeUndefined()
  })
})

describe('config', () => {
  test('the mode defaults to on and reads the four values', async () => {
    expect(parseMode(undefined)).toBe('on')
    expect(parseMode(' OFF ')).toBe('off')
    expect(parseMode('strict')).toBe('strict')
    expect(parseMode('loud')).toBe('on')
  })
  test('the version comes from plugin.json', async () => {
    expect(parseVersion('{"name":"marcketplace","version":"1.3.3"}')).toBe('1.3.3')
    expect(parseVersion('not json')).toBe('unknown')
  })
})
