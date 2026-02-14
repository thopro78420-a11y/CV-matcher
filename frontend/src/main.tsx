import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import { CVLibraryPage } from './pages/CVLibraryPage'
import { RFPPage } from './pages/RFPPage'
import { MatchingPage } from './pages/MatchingPage'

function App() {
  return (
    <BrowserRouter>
      <div style={{ fontFamily: 'Arial', padding: 20 }}>
        <h1>CV Matcher</h1>
        <nav style={{ display: 'flex', gap: 12, marginBottom: 20 }}>
          <Link to="/">CV Library</Link>
          <Link to="/rfps">Appels d'offres</Link>
          <Link to="/matching">Matching</Link>
        </nav>
        <Routes>
          <Route path="/" element={<CVLibraryPage />} />
          <Route path="/rfps" element={<RFPPage />} />
          <Route path="/matching" element={<MatchingPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
