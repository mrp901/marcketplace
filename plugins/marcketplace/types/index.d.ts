// The marcketplace module's session state: what it has worked out about the run
// and what it has seen. Values never hold `undefined`; an absent field is left out.

export type GuardMode = 'off' | 'warn' | 'on' | 'strict'

export type Loaded = { version: string; mode: GuardMode; announced: boolean }

export type MainContext = { unattended: boolean; skill?: string; profileRef?: string }

export type AgentContext = {
  kind: 'handler' | 'reader' | 'other'
  handler?: string
  mode?: string
  unattended: boolean
  budgetToolCalls?: number
  parentAgentId?: string
}

export type StateDocSeen = { bytes: number; topKeys: string[]; runsKeys: string[] }

export type Learned = {
  fallbackChannelId?: string
  feedChannelIds: string[]
  surfaceId?: string
  stateDocs: Record<string, StateDocSeen>
}

declare module 'claude-code' {
  interface PluginState {
    marcketplace: {
      loaded: Loaded
      main: MainContext
      learned: Learned
      agents: StateFamily<AgentContext>
    }
  }
}
