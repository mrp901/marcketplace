// marcketplace observer (1.3.3). Works out where it is running and what it has
// seen, and says so in the transcript. It refuses nothing: the guards that act
// on what it learns arrive in 1.4.0 (docs/plans/guards-mod-build-plan.md).
// Every hook passes its call through unchanged, and a failure in the observer
// is swallowed, so a bug here can never block a routine.

import type { EngineInterface, Register } from 'claude-code'
import type { Learned, Loaded, MainContext } from '../types'
import { parseMode, parseVersion } from './lib/config.ts'
import { classifyDispatch, mainFrom, parseInvocation, skillOf } from './lib/context.ts'
import { dispatchNote, loadNote, profileNote, stateDocNote } from './lib/notes.ts'
import { idArgs, scanProfile, scanStateDoc } from './lib/observe.ts'
import { resultText, stringValues } from './lib/text.ts'

const LOADED = { plugin: 'marcketplace', key: 'loaded' } as const
const MAIN = { plugin: 'marcketplace', key: 'main' } as const
const LEARNED = { plugin: 'marcketplace', key: 'learned' } as const
const AGENTS = { plugin: 'marcketplace', key: 'agents' } as const

type $ = EngineInterface

/** A line in the transcript the model never reads, mirrored to the host's log. */
const note = async ($: $, text: string): Promise<void> => {
  try {
    $.ui.log(text)
  } catch {
    // a host with no log still gets the notice below
  }
  try {
    await $.session.append({ message: { type: 'system', content: [{ type: 'text', text }] } })
  } catch {
    // nowhere to say it; the observer carries on regardless
  }
}

const reported = new Set<string>()

/** Says once per hook that the observer failed there, so a silent transcript is never mistaken for a missing module. */
const report = async ($: $, where: string, err: unknown): Promise<void> => {
  if (reported.has(where)) return
  reported.add(where)
  const reason = err instanceof Error ? err.message : String(err)
  await note($, `marcketplace observer: ${where} observation failed · ${reason.slice(0, 200)}`)
}

/** The mode and version, read once per session; session.start may not have run (tests, a reload). */
const loaded = async ($: $): Promise<Loaded> => {
  const { value } = await $.state.get(LOADED)
  if (value) return value
  let raw: string | undefined
  try {
    raw = await $.env.get('MARCKETPLACE_GUARDS')
  } catch {
    // an environment that cannot be read leaves the default mode
  }
  const mode = parseMode(raw)
  let version = 'unknown'
  try {
    version = parseVersion(String(await $.fs.read(`${$.plugin.root}/.claude-plugin/plugin.json`)))
  } catch {
    // no filesystem (tests) or no manifest: the version stays unknown
  }
  const fresh: Loaded = { version, mode, announced: false }
  await $.state.set(LOADED, fresh)
  return fresh
}

const learned = async ($: $): Promise<Learned> =>
  (await $.state.get(LEARNED)).value ?? { feedChannelIds: [], stateDocs: {} }

const observeCall = async ($: $, e: { tool: string; agentId?: string }, answer: unknown): Promise<void> => {
  const { mode } = await loaded($)
  if (mode === 'off') return

  if (e.tool === 'Skill') {
    const inv = skillOf(e)
    if (inv && e.agentId) {
      const ref = { ...AGENTS, id: e.agentId }
      const { value: agent } = await $.state.get(ref)
      if (agent && !agent.handler) await $.state.set(ref, { ...agent, handler: inv.skill })
    } else if (inv) {
      const { value: main } = await $.state.get(MAIN)
      const next: MainContext = main ? { ...main, skill: inv.skill } : mainFrom(inv)
      await $.state.set(MAIN, next)
    }
  }

  if (answer !== null && typeof answer === 'object' && 'deny' in answer && answer.deny !== undefined) return

  const sent = stringValues(e).join('\n')
  const got = resultText(answer)
  const seen = await learned($)
  let changed = false

  const profile = scanProfile(got)
  if (profile && profile.fallbackChannelId !== seen.fallbackChannelId) {
    seen.fallbackChannelId = profile.fallbackChannelId
    seen.feedChannelIds = profile.feedChannelIds
    if (profile.surfaceId) seen.surfaceId = profile.surfaceId
    changed = true
    await note($, profileNote(profile))
  }

  const doc = scanStateDoc(sent) ?? scanStateDoc(got)
  if (doc) {
    const ids = idArgs(e)
    for (const id of ids.length > 0 ? ids : [`(${e.tool})`]) {
      const isNew = seen.stateDocs[id] === undefined
      seen.stateDocs[id] = doc
      changed = true
      if (isNew) await note($, stateDocNote(id, doc))
    }
  }

  if (changed) await $.state.set(LEARNED, seen)
}

export const register: Register = (on) => {
  on('session.start', async ($, e, next) => {
    try {
      await loaded($)
    } catch {
      // read again on first use
    }
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    const answer = await next(e)
    try {
      const inv = answer.drop === undefined ? parseInvocation(e.text) : undefined
      if (inv) {
        const state = await loaded($)
        const main = mainFrom(inv)
        if (state.mode !== 'off') await $.state.set(MAIN, main)
        if (!state.announced) {
          await $.state.set(LOADED, { ...state, announced: true })
          await note($, loadNote(state.version, state.mode, main))
        }
      }
    } catch (err) {
      // the observer never stands in a prompt's way
      await report($, 'prompt.submit', err)
    }
    return answer
  }).catch(($, e, next) => next(e))

  on('tool.call', async ($, e, next) => {
    const answer = await next(e)
    try {
      await observeCall($, e, answer)
    } catch (err) {
      // an observer that fails leaves the call's answer as it was
      await report($, 'tool.call', err)
    }
    return answer
  }).catch(($, e, next) => next(e))

  on('agent.spawn', async ($, e, next) => {
    const answer = await next(e)
    try {
      const agentId = 'agentId' in answer ? answer.agentId : undefined
      const { mode } = await loaded($)
      if (agentId && mode !== 'off') {
        const parent = e.parentAgentId
          ? (await $.state.get({ ...AGENTS, id: e.parentAgentId })).value?.unattended
          : (await $.state.get(MAIN)).value?.unattended
        const agent = classifyDispatch(e.prompt, parent === true)
        if (e.parentAgentId) agent.parentAgentId = e.parentAgentId
        await $.state.set({ ...AGENTS, id: agentId }, agent)
        if (agent.kind === 'handler') await note($, dispatchNote(agent))
      }
    } catch (err) {
      // a spawn is never held up by the observer
      await report($, 'agent.spawn', err)
    }
    return answer
  }).catch(($, e, next) => next(e))
}

