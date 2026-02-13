import React from 'react'
import ReactDOM from 'react-dom/client'
import { CssBaseline, Container, Typography } from '@mui/material'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <>
      <CssBaseline />
      <Container sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>Fleet Maintenance + Spares Automation</Typography>
        <DashboardPage />
      </Container>
    </>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
