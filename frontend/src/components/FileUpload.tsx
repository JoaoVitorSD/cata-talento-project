import api from '@/lib/api'
import type { ProcessResponse } from '@/types/validation'
import { useCallback, useState } from 'react'

interface FileUploadProps {
    onUploadSuccess: (data: ProcessResponse) => void
    setLoading: (loading: boolean) => void
    setCurrentData: (data: ProcessResponse) => void
}

export default function FileUpload({ onUploadSuccess, setLoading, setCurrentData }: FileUploadProps) {
    const [dragActive, setDragActive] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [saveSuccess, setSaveSuccess] = useState(false)

    const handleDrag = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }, [])

    const processFile = async (file: File) => {
        if (!file.name.endsWith('.pdf')) {
            setError('Por favor, envie um arquivo PDF')
            return
        }
        const formData = new FormData()
        formData.append('file', file)
        setError(null)
        setLoading(true)
        setSaveSuccess(false)

        try {
            const { data } = await api.post<ProcessResponse>('/process-pdf', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })

            // Check if there are any validation errors
            if (Object.keys(data.errors).length > 0) {
                const errorMessages = Object.entries(data.errors)
                    .map(([field, errors]) => `${field}: ${errors.join(', ')}`)
                    .join('; ')
                setError(`Erros de validação: ${errorMessages}`)
            }

            setCurrentData(data)
            onUploadSuccess(data)
        } catch (err) {
            setError('Erro ao processar arquivo. Por favor, tente novamente.')
        } finally {
            setLoading(false)
        }
    }


    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0])
        }
    }, [])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0])
        }
    }

    return (
        <div className="space-y-6">
            <div
                className={`relative rounded-lg border-2 border-dashed p-8 transition-colors
                ${dragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 bg-white'}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleChange}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />

                <div className="text-center">
                    <div className="mx-auto w-16 h-16 mb-4">
                        <svg
                            className={`w-full h-full ${dragActive ? 'text-indigo-500' : 'text-gray-400'}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                            />
                        </svg>
                    </div>
                    <p className="text-lg font-medium text-gray-900">
                        Arraste seu arquivo PDF aqui ou clique para selecionar
                    </p>
                    <p className="mt-1 text-sm text-gray-500">
                        Apenas arquivos PDF são aceitos
                    </p>
                    {error && (
                        <p className="mt-2 text-sm text-red-600">
                            {error}
                        </p>
                    )}
                    {saveSuccess && (
                        <p className="mt-2 text-sm text-green-600">
                            Documento salvo com sucesso!
                        </p>
                    )}
                </div>
            </div>

        </div>
    )
} 