import { useEffect, useState } from 'react'
import { Alert, Card, CardContent, Grid, Typography } from '@mui/material'
import { getDashboard } from '../api/client'

const defaultData = { due_maintenance_count: 0, low_stock_count: 0, open_indent_count: 0 }

export default function DashboardPage() {
  const [data, setData] = useState(defaultData)
  const [error, setError] = useState('')

  useEffect(() => {
    getDashboard().then(setData).catch(() => setError('Login required. Set JWT token in API client for secured endpoints.'))
  }, [])

  return (
    <>
      {error && <Alert severity="warning" sx={{ mb: 2 }}>{error}</Alert>}
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}><Metric title="Due Maintenance" value={data.due_maintenance_count} /></Grid>
        <Grid item xs={12} md={4}><Metric title="Low Stock" value={data.low_stock_count} /></Grid>
        <Grid item xs={12} md={4}><Metric title="Open Indents" value={data.open_indent_count} /></Grid>
      </Grid>
    </>
  )
}

function Metric({ title, value }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="h3">{value}</Typography>
      </CardContent>
    </Card>
  )
}
