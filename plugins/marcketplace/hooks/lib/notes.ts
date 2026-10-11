import type { AgentContext, GuardMode, MainContext, StateDocSeen } from '../../types'
import type { ProfileSeen } from './observe.ts'

const PREFIX = 'marcketplace observer'

const kb = (bytes: number): string => `${(bytes / 1024).toFixed(1)} KB`

const plural = (n: number, one: string, many: string): string => `${n} ${n === 1 ? one : many}`

export const loadNote = (version: string, mode: GuardMode, main: MainContext): string =>
  `${PREFIX} ${version} loaded · mode ${mode} · ${main.unattended ? 'unattended' : 'attended'} run of ${main.skill ?? 'an unnamed skill'}`

export const profileNote = (p: ProfileSeen): string =>
  [
    `${PREFIX}: profile seen`,
    `home channel ${p.fallbackChannelId}`,
    plural(p.feedChannelIds.length, 'feed channel', 'feed channels'),
    `surface ${p.surfaceId ?? 'not found'}`,
  ].join(' · ')

export const stateDocNote = (id: string, seen: StateDocSeen): string =>
  [
    `${PREFIX}: state document seen`,
    id,
    kb(seen.bytes),
    plural(seen.topKeys.length, 'top-level key', 'top-level keys'),
  ].join(' · ')

export const dispatchNote = (agent: AgentContext): string =>
  [
    `${PREFIX}: handler dispatch`,
    agent.handler ?? 'handler not named',
    `mode ${agent.mode ?? 'unknown'}`,
    agent.budgetToolCalls === undefined ? 'no budget' : `budget ${agent.budgetToolCalls} calls`,
  ].join(' · ')
