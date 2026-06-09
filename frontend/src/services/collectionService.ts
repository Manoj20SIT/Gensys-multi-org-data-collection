import type { RunCollectionPayload, RunCollectionResponse } from "../types/RunCollectionTypes";
import authService from "./authService";



export const collectionService = {
  async runCollection(payload: RunCollectionPayload): Promise<RunCollectionResponse> {
    const res = await authService.api.post("/api/run", payload);
    return res.data;
  },
};
