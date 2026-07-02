import { useQuery } from '@tanstack/react-query';
import { childrenService } from '@/core/api/children.service';
import { gamesService } from '@/core/api/games.service';
import { doctorsService } from '@/core/api/doctors.service';
import { parentsService } from '@/core/api/parents.service';
import { queryKeys } from '@/core/constants/queryKeys';
import type { Child, Session, Doctor, Parent, Game } from '@/core/types';
import { ApiResponse } from '@/core/types/api.types';

export type { ApiResponse, Child, Session, Doctor, Parent, Game };

export function useChildren(parentId?: string) {
  const { data: children = [], isLoading, error } = useQuery({
    queryKey: queryKeys.children.list(parentId),
    queryFn: () => childrenService.getChildren(parentId),
    staleTime: 60000, // Smart caching: 1 minute
    refetchOnWindowFocus: true, // Refresh automatically when window is focused
  });

  return { children, loading: isLoading, error };
}

export function useSessions(childId?: string) {
  const { data: sessions = [], isLoading, error } = useQuery({
    queryKey: queryKeys.sessions.list(childId),
    queryFn: () => childrenService.getSessions(childId),
    staleTime: 60000, // Smart caching: 1 minute
    refetchOnWindowFocus: true, // Refresh automatically when window is focused
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
