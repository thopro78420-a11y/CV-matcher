import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Rfp = { rfp_id: string; structured: { role_title: string } }

type MatchResult = {
  candidate_id: string
  candidate_name: string
  score_global: number
  must_found: { count: number; total: number; missing: string[] }
  deductions_applied: { keyword: string; used_form: string }[]
  evidence: { keyword: string; match_type: string; chunk_text_excerpt: string }[]
}

export function MatchingPage() {
  const [rfps, setRfps] = useState<Rfp[]>([])
  const [selected, setSelected] = useState('')
  const [debug, setDebug] = useState(false)
  const [results, setResults] = useState<MatchResult[]>([])

  useEffect(() => {
    api.get('/rfps').then((res) => {
      setRfps(res.data)
      if (res.data.length) setSelected(res.data[0].rfp_id)
    })
  }, [])

  const run = async () => {
    const { data } = await api.post('/match/run', { rfp_id: selected, top_n: 10, debug })
    setResults(data.results)
  }

  return <div>
    <h2>Matching</h2>
    <select value={selected} onChange={(e) => setSelected(e.target.value)}>
      {rfps.map((r) => <option key={r.rfp_id} value={r.rfp_id}>{r.structured?.role_title || r.rfp_id}</option>)}
    </select>
    <label><input type="checkbox" checked={debug} onChange={(e) => setDebug(e.target.checked)} /> Debug</label>
    <button onClick={run}>Matcher</button>
    <table border={1} cellPadding={6} style={{ marginTop: 12 }}>
      <thead><tr><th>Candidat</th><th>Score</th><th>Must</th><th>Manquants</th><th>Déductions</th></tr></thead>
      <tbody>
      {results.map((r) => (
        <tr key={r.candidate_id}>
          <td>{r.candidate_name}</td><td>{r.score_global}%</td>
          <td>{r.must_found.count}/{r.must_found.total}</td>
          <td>{r.must_found.missing.join(', ')}</td>
          <td>{r.deductions_applied.map((d) => `${d.keyword}->${d.used_form}`).join('; ')}</td>
        </tr>
      ))}
      </tbody>
    </table>
    {debug && results[0] && (
      <div>
        <h3>Preuves ({results[0].candidate_name})</h3>
        <ul>{results[0].evidence.map((e, i) => <li key={i}><b>{e.keyword}</b> [{e.match_type}] - {e.chunk_text_excerpt}</li>)}</ul>
      </div>
    )}
  </div>
}
