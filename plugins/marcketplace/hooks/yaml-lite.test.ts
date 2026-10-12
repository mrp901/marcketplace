import { describe, expect, test } from 'claude-code/testing'
import { childKeys, entriesUnder, fenceBodies, topLevelKeys, utf8Bytes } from './lib/yaml-lite.ts'

const YAML = ['# a comment: not a key', 'a: 1', 'b:', '  c: 2   # trailing', '  d:', '    e: 3', 'f: {}', ''].join('\n')

describe('yaml-lite', () => {
  test('top-level keys skip comments and nested keys', async () => {
    expect(topLevelKeys(YAML)).toEqual(['a', 'b', 'f'])
  })
  test('entries under a key stop at its siblings and drop comments', async () => {
    expect(entriesUnder(YAML, 'b')).toEqual([
      { key: 'c', value: '2' },
      { key: 'd', value: '' },
    ])
    expect(childKeys(YAML, 'f')).toEqual([])
    expect(childKeys(YAML, 'missing')).toEqual([])
  })
  test('fenced and CDATA bodies are both found', async () => {
    expect(fenceBodies('x\n```yaml\na: 1\n```\ny')).toEqual(['a: 1\n'])
    expect(fenceBodies('<![CDATA[a: 1]]>')).toEqual(['a: 1'])
    expect(fenceBodies('no yaml here')).toEqual([])
  })
  test('an emoji is four bytes', async () => {
    expect(utf8Bytes('ok ✅')).toBe(6)
    expect(utf8Bytes('\u{1F600}')).toBe(4)
  })
})
