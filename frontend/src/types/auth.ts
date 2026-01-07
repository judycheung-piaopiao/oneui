export interface User {
  user_id: number;
  first_name: string;
  last_name: string;
  email: string;
  active: boolean;
  updated_by?: number;
  team_name: string;
  role_name: string;
  accessList?: Record<string, string[]>;
}

export const RoleName = {
  ADMIN: "ADMIN",
  SUPER_ADMIN: "SUPER_ADMIN",
  MODERATOR: "MODERATOR",
  TEAM_OWNER: "TEAM_OWNER",
  TEAM_MEMBER: "TEAM_MEMBER",
} as const;

export type RoleName = typeof RoleName[keyof typeof RoleName];

export function isAdminRole(role: string): boolean {
  const adminRoles = [
    RoleName.ADMIN,
    RoleName.SUPER_ADMIN,
    RoleName.MODERATOR,
  ];
  return adminRoles.includes(role as any);
}
