import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,  // 2 minutes — analysis can take a while
  headers: {
    'Content-Type': 'application/json',
  },
})

export const analyzeStock = async (ticker) => {
  const response = await api.post('/analyze', { ticker })
  return response.data
}

export const downloadPDF = async (ticker) => {
  const response = await api.post('/analyze/pdf',
    { ticker },
    { responseType: 'blob' }
  )

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `${ticker.toUpperCase()}_equity_research.pdf`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api