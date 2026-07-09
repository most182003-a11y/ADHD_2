import { useQuery } from '@tanstack/react-query';
import { childrenService } from '@/core/api/children.service';
import { gamesService } from '@/core/api/games.service';
import { doctorsService } from '@/core/api/doctors.service';
import { parentsService } from '@/core/api/parents.service';
import { getChildAnalyses } from '@/core/api/analysis.service';
import { queryKeys } from '@/core/constants/queryKeys';
import type { Child, Session, Doctor, Parent, Game } from '@/core/types';
import type { AIAnalysisWithGame } from '@/core/types/analysis.types';
import { ApiResponse } from '@/core/types/api.types';

export type { ApiResponse, Child, Session, Doctor, Parent, Game, AIAnalysisWithGame };

export function useChildren(parentId?: string) {
  const { data: children = [], isLoading, error } = useQuery({
    queryKey: queryKeys.children.list(parentId),
    queryFn: () => childrenService.getChildren(parentId),
    staleTime: 60000,
    refetchOnWindowFocus: true,
  });

  return { children, loading: isLoading, error };
}

export function useSessions(childId?: string) {
  const { data: sessions = [], isLoading, error } = useQuery({
    queryKey: queryKeys.sessions.list(childId),
    queryFn: () => childrenService.getSessions(childId),
    staleTime: 60000,
    refetchOnWindowFocus: true,
  });

  return { sessions, loading: isLoading, error };
}

export function useDoctors() {
  const { data: doctors = [], isLoading, error } = useQuery({
    queryKey: queryKeys.doctors.list(),
    queryFn: doctorsService.getDoctors,
  });

  return { doctors, loading: isLoading, error };
}

export function useParents() {
  const { data: parents = [], isLoading, error } = useQuery({
    queryKey: queryKeys.parents.list(),
    queryFn: parentsService.getParents,
  });

  return { parents, loading: isLoading, error };
}

export function useGames() {
  const { data: games = [], isLoading, error } = useQuery({
    queryKey: queryKeys.games.list(),
    queryFn: gamesService.getGames,
  });

  return { games, loading: isLoading, error };
}

export function useChildAnalyses(childId?: string) {
  const { data: analyses = [], isLoading, error } = useQuery({
    queryKey: queryKeys.analyses.byChild(childId),
    queryFn: () => getChildAnalyses(childId!),
    enabled: !!childId,
    staleTime: 30000, // 30 seconds — AI results update after each session
    refetchOnWindowFocus: true,
  });

  return { analyses, loading: isLoading, error };
}
