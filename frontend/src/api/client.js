import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
})

export const getDashboard = async () => (await api.get('/dashboard')).data
export const getDueMaintenance = async () => (await api.get('/maintenance/due')).data

export default api
