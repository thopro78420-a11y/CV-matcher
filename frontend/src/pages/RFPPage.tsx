import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Rfp = { rfp_id: string; filename?: string; structured: { role_title: string } }

export function RFPPage() {
  const [items, setItems] = useState<Rfp[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [text, setText] = useState('')

  const load = async () => {
    const { data } = await api.get('/rfps')
    setItems(data)
  }
  useEffect(() => { load() }, [])

  const create = async () => {
    const form = new FormData()
    if (file) form.append('file', file)
    if (text) form.append('text', text)
    await api.post('/rfps', form)
    setText('')
    setFile(null)
    await load()
  }

  return <div>
    <h2>Appels d'offres</h2>
    <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
    <textarea rows={8} cols={80} value={text} onChange={(e) => setText(e.target.value)} placeholder="Collez le texte AO" />
    <br /><button onClick={create}>Ajouter AO</button>
    <ul>{items.map((r) => <li key={r.rfp_id}>{r.structured?.role_title || r.filename || r.rfp_id}</li>)}</ul>
  </div>
}
