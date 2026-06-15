export type RunCollectionPayload = {
  interval: string;
  fields?: string[];
};

export type RunCollectionResponse = {
  total_orgs: number;
  mode: string;
  requested_fields: string[];
  results: Array<{
    org_name: string;
    
    metrics: Record<string, any> | null;
  }>;
  file_name?: string;
  download_url?: string;
  message?: string | null;
};