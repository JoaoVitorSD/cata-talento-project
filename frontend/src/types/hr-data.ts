export interface WorkExperience {
    company: string;
    position: string;
    start_date: string;
    end_date?: string;
    current_job: boolean;
    description: string;
    achievements: string[];
    technologies_used: string[];
}

export interface HRData {
    name: string;
    cpf: string;
    position?: string;
    salary?: number | null;
    contract_type?: string;
    main_skills?: string[];
    hard_skills?: string[];
    work_experience: WorkExperience[];
} 