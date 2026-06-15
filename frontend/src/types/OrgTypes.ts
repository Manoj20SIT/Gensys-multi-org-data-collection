export type Org = {
  org_name: string;
  
    region?: string;
    api_base_url?: string;
    client_id?: string;
    client_secret?: string;

};

export type ListOrgsResponse = {
  total_orgs: number;
  orgs: Org[];
};