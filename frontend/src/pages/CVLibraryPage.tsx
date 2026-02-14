import { useEffect, useState } from 'react'
import { api } from '../api/client'

type Candidate = { candidate_id: string; name: string; status: string }

export function CVLibraryPage() {
  const [items, setItems] = useState<Candidate[]>([])
  const [files, setFiles] = useState<FileList | null>(null)

  const load = async () => {
    const { data } = await api.get('/cvs')
    setItems(data)
  }

  useEffect(() => { load() }, [])

  const upload = async () => {
    if (!files) return
    const form = new FormData()
    Array.from(files).forEach((f) => form.append('files', f))
    await api.post('/cvs/upload', form)
    await load()
  }

  const remove = async (id: string) => {
    await api.delete(`/cvs/${id}`)
    await load()
  }

  return <div>
    <h2>CV Library</h2>
    <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
    <button onClick={upload}>Importer CV</button>
    <ul>
      {items.map((c) => <li key={c.candidate_id}>{c.name} ({c.status}) <button onClick={() => remove(c.candidate_id)}>Supprimer</button></li>)}
    </ul>
  </div>
}
