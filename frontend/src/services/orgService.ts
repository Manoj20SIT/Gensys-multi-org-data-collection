import type { ListOrgsResponse, Org } from "../types/OrgTypes";
import authService from "./authService";



export const orgService = {
  async getOrgs(): Promise<ListOrgsResponse> {
    const res = await authService.api.get<ListOrgsResponse>("/api/orgs");
    return res.data;
  },

  async getOrgByName(orgName: string): Promise<Org> {
    const res = await authService.api.get<Org>(`/api/orgs/${encodeURIComponent(orgName)}`);
    return res.data;
  },

  async deleteOrg(orgName: string): Promise<void> {
    await authService.api.delete(`/api/orgs/${encodeURIComponent(orgName)}`);
  },

  // optional, when your backend supports it
  async updateOrg(orgName: string, payload: Partial<Org>): Promise<Org> {
    const res = await authService.api.put<Org>(
      `/api/orgs/${encodeURIComponent(orgName)}`,
      payload
    );
    return res.data;
  },

  async createOrg(payload: any) {
  console.log(" the requested data is ",payload)
  const res = await authService.api.post("/api/orgs", payload);
  return res.data;
}

};
