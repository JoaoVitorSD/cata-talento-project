import type { HRData } from './hr-data'

export interface ValidationErrors {
    [key: string]: string[]
}

export interface ProcessResponse {
    hr_data: HRData | null
    errors: ValidationErrors
} 