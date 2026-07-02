export const queryKeys = {
  children: {
    all: ['children'] as const,
    list: (parentId?: string) => [...queryKeys.children.all, 'list', parentId || 'all'] as const,
  },
  sessions: {
    all: ['sessions'] as const,
    list: (childId?: string) => [...queryKeys.sessions.all, 'list', childId || 'all'] as const,
  },
  doctors: {
    all: ['doctors'] as const,
    list: () => [...queryKeys.doctors.all, 'list'] as const,
  },
  parents: {
    all: ['parents'] as const,
    list: () => [...queryKeys.parents.all, 'list'] as const,
  },
  games: {
    all: ['games'] as const,
    list: () => [...queryKeys.games.all, 'list'] as const,
  }
} as const;
