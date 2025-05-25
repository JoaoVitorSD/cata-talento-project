import { useEffect, useState } from 'react'
import type { HRData, WorkExperience } from '../types/hr-data'

interface ValidationErrors {
    [key: string]: string[]
}

interface ProcessResponse {
    hr_data: HRData | null
    errors: ValidationErrors
}

interface ResultDisplayProps {
    data: ProcessResponse
    onDataChange: (data: ProcessResponse) => void
}

// Helper function to create a valid HRData object
const createHRData = (data: Partial<HRData>): HRData => {
    return {
        name: data.name || '',
        cpf: data.cpf || '',
        date: data.date || '',
        position: data.position,
        department: data.department,
        salary: data.salary ?? null,
        contract_type: data.contract_type,
        start_date: data.start_date,
        main_skills: data.main_skills || [],
        hard_skills: data.hard_skills || [],
        work_experience: data.work_experience || []
    }
}

// Helper function to update HRData field
const updateHRDataField = (data: HRData, field: keyof HRData, value: any): HRData => {
    const updatedData = { ...data }

    // Handle different field types
    if (field === 'salary') {
        updatedData[field] = value === '' ? null : Number(value)
    } else if (field === 'work_experience') {
        updatedData[field] = value as WorkExperience[]
    } else if (field === 'main_skills' || field === 'hard_skills') {
        updatedData[field] = value as string[]
    } else {
        updatedData[field] = value as string
    }

    return updatedData
}

export default function ResultDisplay({ data, onDataChange }: ResultDisplayProps) {
    const [isEditing, setIsEditing] = useState(false)
    const [editableData, setEditableData] = useState<HRData | null>(data.hr_data ? createHRData(data.hr_data) : null)
    const [validationErrors, setValidationErrors] = useState<ValidationErrors>(data.errors??{})
    const [newSkill, setNewSkill] = useState({ main: '', hard: '' })
    const [newExperience, setNewExperience] = useState<WorkExperience>({
        company: '',
        position: '',
        start_date: '',
        end_date: '',
        current_job: false,
        description: '',
        achievements: [],
        technologies_used: []
    })
    const [newAchievement, setNewAchievement] = useState('')
    const [newTechnology, setNewTechnology] = useState('')

    useEffect(() => {
        // Fetch template data when component mounts and no data is provided
        if (!data.hr_data?.name && !data.hr_data?.cpf) {
            fetch('http://localhost:8000/api/v1/template')
                .then(response => response.json())
                .then(templateData => {
                    const response: ProcessResponse = {
                        hr_data: createHRData(templateData),
                        errors: {}
                    }
                    setEditableData(response.hr_data)
                    onDataChange(response)
                })
                .catch(error => console.error('Error fetching template:', error))
        } else if (data.hr_data) {
            setEditableData(createHRData(data.hr_data))
            setValidationErrors(data.errors)
        }
    }, [data, onDataChange])

    const handleInputChange = (field: keyof HRData, value: any) => {
        if (!editableData) return

        const updatedData = updateHRDataField(editableData, field, value)
        setEditableData(updatedData)

        // Clear validation error for this field when user makes changes
        if (validationErrors[field]) {
            const newErrors = { ...validationErrors }
            delete newErrors[field]
            setValidationErrors(newErrors)
        }
    }

    const handleSaveChanges = () => {
        if (!editableData) return

        // Create new response object with updated data
        const updatedResponse: ProcessResponse = {
            hr_data: editableData,
            errors: validationErrors
        }

        onDataChange(updatedResponse)
        setIsEditing(false)
    }

    const addSkill = (type: 'main_skills' | 'hard_skills') => {
        const skillValue = type === 'main_skills' ? newSkill.main : newSkill.hard
        if (!skillValue.trim()) return

        setEditableData(prev => ({
            ...prev,
            [type]: [...(prev[type] || []), skillValue.trim()]
        }))
        setNewSkill(prev => ({ ...prev, [type === 'main_skills' ? 'main' : 'hard']: '' }))
    }

    const removeSkill = (type: 'main_skills' | 'hard_skills', index: number) => {
        setEditableData(prev => ({
            ...prev,
            [type]: (prev[type] || []).filter((_, i) => i !== index)
        }))
    }

    const addWorkExperience = () => {
        if (!newExperience.company || !newExperience.position || !newExperience.description) return

        setEditableData(prev => ({
            ...prev,
            work_experience: [...prev.work_experience, { ...newExperience }]
        }))
        setNewExperience({
            company: '',
            position: '',
            start_date: '',
            end_date: '',
            current_job: false,
            description: '',
            achievements: [],
            technologies_used: []
        })
    }

    const removeWorkExperience = (index: number) => {
        setEditableData(prev => ({
            ...prev,
            work_experience: prev.work_experience.filter((_, i) => i !== index)
        }))
    }

    const addAchievement = (experienceIndex: number) => {
        if (!newAchievement.trim()) return

        setEditableData(prev => {
            const newWorkExperience = [...prev.work_experience]
            newWorkExperience[experienceIndex].achievements.push(newAchievement.trim())
            return { ...prev, work_experience: newWorkExperience }
        })
        setNewAchievement('')
    }

    const addTechnology = (experienceIndex: number) => {
        if (!newTechnology.trim()) return

        setEditableData(prev => {
            const newWorkExperience = [...prev.work_experience]
            newWorkExperience[experienceIndex].technologies_used.push(newTechnology.trim())
            return { ...prev, work_experience: newWorkExperience }
        })
        setNewTechnology('')
    }

    const basicFields = [
        { label: 'Nome', field: 'name' as keyof HRData, type: 'text', required: true },
        { label: 'CPF', field: 'cpf' as keyof HRData, type: 'text', required: true },
        { label: 'Data', field: 'date' as keyof HRData, type: 'datetime-local', required: true },
        { label: 'Cargo', field: 'position' as keyof HRData, type: 'text', required: false },
        { label: 'Departamento', field: 'department' as keyof HRData, type: 'text', required: false },
        { label: 'Salário', field: 'salary' as keyof HRData, type: 'number', required: false },
        { label: 'Tipo de Contrato', field: 'contract_type' as keyof HRData, type: 'text', required: false },
        { label: 'Data de Início', field: 'start_date' as keyof HRData, type: 'datetime-local', required: false },
    ]

    if (!editableData) {
        return <div>Carregando...</div>
    }

    const renderFieldValue = (field: keyof HRData) => {
        const value = editableData[field]
        if (value === null || value === undefined) {
            return 'Não informado'
        }
        if (Array.isArray(value)) {
            return value.join(', ')
        }
        return value.toString()
    }

    return (
        <div className="bg-white rounded-lg shadow-lg p-6 animate-fade-in space-y-8 w-full">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-semibold text-indigo-900">
                    {isEditing ? 'Editar Informações' : 'Informações do Documento'}
                </h2>
                <button
                    onClick={() => isEditing ? handleSaveChanges() : setIsEditing(true)}
                    className={`px-4 py-2 rounded-lg font-medium text-white transition-colors
                        ${isEditing ? 'bg-green-600 hover:bg-green-700' : 'bg-indigo-600 hover:bg-indigo-700'}`}
                >
                    {isEditing ? 'Salvar Alterações' : 'Editar'}
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {basicFields.map(({ label, field, type, required }) => (
                    <div
                        key={field}
                        className={`bg-gray-50 rounded-lg p-4 border ${validationErrors[field] ? 'border-red-300' : 'border-gray-100'
                            }`}
                    >
                        <p className="text-sm font-medium text-gray-500">
                            {label}
                            {required && <span className="text-red-500 ml-1">*</span>}
                        </p>
                        {isEditing ? (
                            <div>
                                <input
                                    type={type}
                                    value={editableData[field]?.toString() || ''}
                                    onChange={(e) => handleInputChange(field, e.target.value)}
                                    className={`mt-1 w-full p-2 border rounded-md focus:ring-2 focus:ring-indigo-500 ${validationErrors[field] ? 'border-red-300' : ''
                                        }`}
                                    required={required}
                                />
                                {validationErrors[field] && (
                                    <p className="mt-1 text-sm text-red-600">
                                        {validationErrors[field].join(', ')}
                                    </p>
                                )}
                            </div>
                        ) : (
                            <p className="mt-1 text-lg text-gray-900">
                                {renderFieldValue(field)}
                            </p>
                        )}
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Main Skills */}
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                    <p className="text-sm font-medium text-blue-700">Competências Comportamentais</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                        {editableData.main_skills?.map((skill, index) => (
                            <span
                                key={index}
                                className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 flex items-center"
                            >
                                {skill}
                                {isEditing && (
                                    <button
                                        onClick={() => removeSkill('main_skills', index)}
                                        className="ml-2 text-blue-600 hover:text-blue-800"
                                    >
                                        ×
                                    </button>
                                )}
                            </span>
                        ))}
                        {isEditing && (
                            <div className="flex gap-2 mt-2 w-full">
                                <input
                                    type="text"
                                    value={newSkill.main}
                                    onChange={(e) => setNewSkill(prev => ({ ...prev, main: e.target.value }))}
                                    placeholder="Adicionar competência"
                                    className="flex-1 p-2 border rounded-md"
                                    onKeyPress={(e) => e.key === 'Enter' && addSkill('main_skills')}
                                />
                                <button
                                    onClick={() => addSkill('main_skills')}
                                    className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                                >
                                    Adicionar
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Hard Skills */}
                <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                    <p className="text-sm font-medium text-green-700">Competências Técnicas</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                        {editableData.hard_skills?.map((skill, index) => (
                            <span
                                key={index}
                                className="px-3 py-1 rounded-full text-sm bg-green-100 text-green-800 flex items-center"
                            >
                                {skill}
                                {isEditing && (
                                    <button
                                        onClick={() => removeSkill('hard_skills', index)}
                                        className="ml-2 text-green-600 hover:text-green-800"
                                    >
                                        ×
                                    </button>
                                )}
                            </span>
                        ))}
                        {isEditing && (
                            <div className="flex gap-2 mt-2 w-full">
                                <input
                                    type="text"
                                    value={newSkill.hard}
                                    onChange={(e) => setNewSkill(prev => ({ ...prev, hard: e.target.value }))}
                                    placeholder="Adicionar competência técnica"
                                    className="flex-1 p-2 border rounded-md"
                                    onKeyPress={(e) => e.key === 'Enter' && addSkill('hard_skills')}
                                />
                                <button
                                    onClick={() => addSkill('hard_skills')}
                                    className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700"
                                >
                                    Adicionar
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Work Experience Section */}
            <div className="bg-purple-50 rounded-lg p-6 border border-purple-100">
                <h3 className="text-xl font-semibold text-purple-900 mb-4">Experiência Profissional</h3>
                {validationErrors['work_experience'] && (
                    <p className="mb-4 text-sm text-red-600">
                        {validationErrors['work_experience'].join(', ')}
                    </p>
                )}

                {editableData.work_experience?.map((exp, index) => (
                    <div
                        key={index}
                        className={`mb-6 p-4 bg-white rounded-lg shadow ${validationErrors[`work_experience.${index}`] ? 'border border-red-300' : ''
                            }`}
                    >
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-medium">{exp.company}</h4>
                                <p className="text-gray-600">{exp.position}</p>
                            </div>
                            {isEditing && (
                                <button
                                    onClick={() => removeWorkExperience(index)}
                                    className="text-red-600 hover:text-red-800"
                                >
                                    Remover
                                </button>
                            )}
                        </div>

                        <div className="mt-2 grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-sm text-gray-500">Data de Início</p>
                                <p>{new Date(exp.start_date).toLocaleDateString()}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">Data de Término</p>
                                <p>{exp.current_job ? 'Atual' : exp.end_date ? new Date(exp.end_date).toLocaleDateString() : 'Não informado'}</p>
                            </div>
                        </div>

                        <div className="mt-4">
                            <p className="text-sm text-gray-500">Descrição</p>
                            <p className="mt-1">{exp.description}</p>
                        </div>

                        <div className="mt-4">
                            <p className="text-sm text-gray-500">Conquistas</p>
                            <ul className="list-disc list-inside mt-1">
                                {exp.achievements?.map((achievement, i) => (
                                    <li key={i}>{achievement}</li>
                                ))}
                            </ul>
                        </div>

                        <div className="mt-4">
                            <p className="text-sm text-gray-500">Tecnologias Utilizadas</p>
                            <div className="flex flex-wrap gap-2 mt-1">
                                {exp.technologies_used.map((tech, i) => (
                                    <span key={i} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                                        {tech}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                ))}

                {isEditing && (
                    <div className="mt-4 p-4 bg-white rounded-lg shadow">
                        <h4 className="text-lg font-medium mb-4">Adicionar Nova Experiência</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <input
                                type="text"
                                placeholder="Empresa"
                                value={newExperience.company}
                                onChange={(e) => setNewExperience(prev => ({ ...prev, company: e.target.value }))}
                                className="p-2 border rounded-md"
                            />
                            <input
                                type="text"
                                placeholder="Cargo"
                                value={newExperience.position}
                                onChange={(e) => setNewExperience(prev => ({ ...prev, position: e.target.value }))}
                                className="p-2 border rounded-md"
                            />
                            <input
                                type="date"
                                placeholder="Data de Início"
                                value={newExperience.start_date}
                                onChange={(e) => setNewExperience(prev => ({ ...prev, start_date: e.target.value }))}
                                className="p-2 border rounded-md"
                            />
                            <div className="flex items-center gap-4">
                                <input
                                    type="date"
                                    placeholder="Data de Término"
                                    value={newExperience.end_date}
                                    onChange={(e) => setNewExperience(prev => ({ ...prev, end_date: e.target.value }))}
                                    disabled={newExperience.current_job}
                                    className="p-2 border rounded-md flex-1"
                                />
                                <label className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        checked={newExperience.current_job}
                                        onChange={(e) => setNewExperience(prev => ({
                                            ...prev,
                                            current_job: e.target.checked,
                                            end_date: e.target.checked ? '' : prev.end_date
                                        }))}
                                        className="rounded text-purple-600"
                                    />
                                    <span className="text-sm">Emprego Atual</span>
                                </label>
                            </div>
                            <textarea
                                placeholder="Descrição"
                                value={newExperience.description}
                                onChange={(e) => setNewExperience(prev => ({ ...prev, description: e.target.value }))}
                                className="p-2 border rounded-md md:col-span-2"
                                rows={3}
                            />
                            <div className="md:col-span-2">
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        placeholder="Conquista"
                                        value={newAchievement}
                                        onChange={(e) => setNewAchievement(e.target.value)}
                                        className="p-2 border rounded-md flex-1"
                                    />
                                    <button
                                        onClick={() => {
                                            if (newAchievement.trim()) {
                                                setNewExperience(prev => ({
                                                    ...prev,
                                                    achievements: [...prev.achievements, newAchievement.trim()]
                                                }))
                                                setNewAchievement('')
                                            }
                                        }}
                                        className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                                    >
                                        Adicionar Conquista
                                    </button>
                                </div>
                                {newExperience.achievements.length > 0 && (
                                    <ul className="list-disc list-inside mt-2">
                                        {newExperience.achievements.map((achievement, i) => (
                                            <li key={i}>{achievement}</li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                            <div className="md:col-span-2">
                                <div className="flex gap-2">
                                    <input
                                        type="text"
                                        placeholder="Tecnologia"
                                        value={newTechnology}
                                        onChange={(e) => setNewTechnology(e.target.value)}
                                        className="p-2 border rounded-md flex-1"
                                    />
                                    <button
                                        onClick={() => {
                                            if (newTechnology.trim()) {
                                                setNewExperience(prev => ({
                                                    ...prev,
                                                    technologies_used: [...prev.technologies_used, newTechnology.trim()]
                                                }))
                                                setNewTechnology('')
                                            }
                                        }}
                                        className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                                    >
                                        Adicionar Tecnologia
                                    </button>
                                </div>
                                {newExperience.technologies_used.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {newExperience.technologies_used.map((tech, i) => (
                                            <span key={i} className="px-2 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                                                {tech}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                        <button
                            onClick={addWorkExperience}
                            className="mt-4 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 w-full"
                        >
                            Adicionar Experiência
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}

// Add fade-in animation
const style = document.createElement('style')
style.textContent = `
  @keyframes fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .animate-fade-in {
    animation: fade-in 0.3s ease-out forwards;
  }
`
document.head.appendChild(style) 