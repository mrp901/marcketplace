import type { AgentContext, MainContext } from '../../types'

export type Invocation = { skill: string; unattended: boolean; profileRef?: string }

const SKILL = /\/?marcketplace:([a-z][a-z0-9-]*)/
// The literal token only, never a word that contains it (onboarding step 0).
const UNATTENDED = /(?<![\w-])unattended(?![\w-])/
const PROFILE = /(?<![\w-])profile=(\S+)/

/** A prompt or skill call that names one of this plugin's skills, or undefined. */
export const parseInvocation = (text: string): Invocation | undefined => {
  const skill = SKILL.exec(text)?.[1]
  if (!skill) return undefined
  const unattended = UNATTENDED.test(text)
  const profileRef = PROFILE.exec(text)?.[1]
  return profileRef ? { skill, unattended, profileRef } : { skill, unattended }
}

export const mainFrom = (inv: Invocation): MainContext =>
  inv.profileRef
    ? { unattended: inv.unattended, skill: inv.skill, profileRef: inv.profileRef }
    : { unattended: inv.unattended, skill: inv.skill }

const MODE = /^\s*mode:\s*([a-z][a-z-]*)\s*$/m
const ITEM = /^\s*item:\s*$/m
const BUDGET = /^\s*budget:.*\btool_calls:\s*(\d+)/m

/**
 * What a subagent is, from the prompt it was spawned with. A hub dispatch
 * carries the payload's `item:` and `mode:` lines and the `unattended` token
 * (`shared/handler-contract.md`); a subagent of an unattended run that is not a
 * dispatch is a reader; anything else is other.
 */
export const classifyDispatch = (prompt: string, parentUnattended: boolean): AgentContext => {
  const mode = MODE.exec(prompt)?.[1]
  const unattended = UNATTENDED.test(prompt) || parentUnattended
  if (mode && ITEM.test(prompt) && UNATTENDED.test(prompt)) {
    const ctx: AgentContext = { kind: 'handler', mode, unattended: true }
    const handler = SKILL.exec(prompt)?.[1]
    if (handler) ctx.handler = handler
    const budget = BUDGET.exec(prompt)?.[1]
    if (budget) ctx.budgetToolCalls = Number(budget)
    return ctx
  }
  return { kind: parentUnattended ? 'reader' : 'other', unattended }
}

/** The skill a Skill tool call names, when it is one of this plugin's. */
export const skillOf = (input: unknown): Invocation | undefined => {
  if (input === null || typeof input !== 'object') return undefined
  const { skill, args } = input as { skill?: unknown; args?: unknown }
  if (typeof skill !== 'string' || !skill.startsWith('marcketplace:')) return undefined
  return parseInvocation(`/${skill} ${typeof args === 'string' ? args : ''}`)
}
