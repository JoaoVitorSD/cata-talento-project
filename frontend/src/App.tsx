import { useState } from 'react'
import { ToastContainer, toast } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import FileUpload from './components/FileUpload'
import ResultDisplay from './components/ResultDisplay'
import api from './lib/api'
import type { ProcessResponse } from './types/validation'

function App() {
  const [hrData, setHRData] = useState<ProcessResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSaveToMongoDB = async () => {
    if (!hrData?.hr_data) return

    setLoading(true)

    try {
      const { data } = await api.post('/store-document', hrData.hr_data)
      toast.success(`Documento enviado com sucesso! ID: ${data.document_id}`)
    } catch (error) {
      toast.error('Falha ao enviar documento. Por favor, tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleDataChange = (newData: ProcessResponse) => {
    setHRData(newData)
    toast.info('Informações atualizadas')
  }

  return (
    <div className="min-h-screen w-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="colored"
      />
      <div className="max-w-7xl mx-auto p-8">
        <h1 className="text-4xl font-bold text-center mb-2 text-indigo-900">
          CataTalento
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Faça upload dos seus documentos ou insira manualmente as informações do candidato
        </p>

        <div className="space-y-8">
          <FileUpload onUploadSuccess={setHRData} setLoading={setLoading} setCurrentData={setHRData} />
          {loading && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
              <p className="mt-4 text-indigo-600">Processando seu documento...</p>
            </div>
          )}
          {hrData && (
            <>
              <ResultDisplay data={hrData} onDataChange={handleDataChange} />
              <div className="flex flex-col items-center space-y-4">
                <button
                  onClick={handleSaveToMongoDB}
                  disabled={loading}
                  className={`px-6 py-3 rounded-lg font-medium text-white transition-colors
                    ${loading
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700'
                    }`}
                >
                  {loading ? 'Enviando...' : 'Enviar'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
