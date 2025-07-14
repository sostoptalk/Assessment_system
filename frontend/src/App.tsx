import { Routes, Route, Navigate } from 'react-router-dom'
import AdminLayout from './layouts/AdminLayout'
import ParticipantLayout from './layouts/ParticipantLayout'
import Login from './pages/Login'
import TestPage from './pages/TestPage'
import './App.css'

function App() {
    return (
        <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/admin/*" element={<AdminLayout />} />
            <Route path="/participant/*" element={<ParticipantLayout />} />
            <Route path="/test" element={<TestPage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
    )
}

export default App 