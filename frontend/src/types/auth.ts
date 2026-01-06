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

export enum RoleName {
  ADMIN = "ADMIN",
  SUPER_ADMIN = "SUPER_ADMIN",
  MODERATOR = "MODERATOR",
  TEAM_OWNER = "TEAM_OWNER",
  TEAM_MEMBER = "TEAM_MEMBER",
}

export function isAdminRole(role: string): boolean {
  return [
    RoleName.ADMIN,
    RoleName.SUPER_ADMIN,
    RoleName.MODERATOR,
  ].includes(role as RoleName);
}
