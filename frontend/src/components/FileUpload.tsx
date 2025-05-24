import type { HRData } from '@/types/hr-data'
import { useCallback, useState } from 'react'

interface FileUploadProps {
    onUploadSuccess: (data: HRData) => void
    setLoading: (loading: boolean) => void
    setCurrentData: (data: HRData) => void
}

export default function FileUpload({ onUploadSuccess, setLoading, setCurrentData }: FileUploadProps) {
    const [dragActive, setDragActive] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [currentFile, setCurrentFile] = useState<File | null>(null)
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

        setCurrentFile(file)
        const formData = new FormData()
        formData.append('file', file)
        setError(null)
        setLoading(true)
        setSaveSuccess(false)

        try {
            const response = await fetch('http://localhost:8000/api/v1/process-pdf', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Falha ao processar arquivo')
            }

            const data = await response.json()
            setCurrentData(data)
            onUploadSuccess(data)
        } catch (err) {
            setError('Erro ao processar arquivo. Por favor, tente novamente.')
        } finally {
            setLoading(false)
        }
    }

    const requestSummary = async () => {
        if (!currentFile) {
            setError('Please upload a file first')
            return
        }

        setLoading(true)
        const formData = new FormData()
        formData.append('file', currentFile)

        try {
            const response = await fetch('http://localhost:8000/summarize-pdf', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Failed to get summary')
            }

            const data = await response.json()
            onUploadSuccess(data)
        } catch (err) {
            setError('Error getting summary. Please try again.')
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

            {currentFile && (
                <button
                    onClick={requestSummary}
                    className="w-full py-3 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center justify-center space-x-2"
                >
                    <svg
                        className="w-5 h-5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                    </svg>
                    <span>Get Document Summary</span>
                </button>
            )}
        </div>
    )
} 