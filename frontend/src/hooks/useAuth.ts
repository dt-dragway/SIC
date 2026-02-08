'use client';

import { useAuthContext } from '../context/AuthContext';

/**
 * useAuth hook (Bridge to AuthContext)
 * Now shares global state instead of creating local instances.
 */
export function useAuth() {
    return useAuthContext();
}
