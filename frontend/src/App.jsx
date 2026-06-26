import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import rehypeRaw from 'rehype-raw'

function App() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  
  const [portalName, setPortalName] = useState('MINECRAFT SERVER')
  const [instructions, setInstructions] = useState('')

  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        if (data.portal_name) setPortalName(data.portal_name)
        if (data.instructions) setInstructions(data.instructions)
      })
      .catch(err => console.error("Failed to load config:", err))
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim()) return

    setLoading(true)
    setMessage(null)
    setError(null)

    try {
      const response = await fetch('/api/whitelist', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Something went wrong')
      }

      setMessage(data.message)
      setUsername('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="w-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl shadow-2xl overflow-hidden transition-all duration-300">
        
        {/* Header */}
        <div className="bg-[#4e8036] bg-opacity-80 p-6 border-b border-[#866043]">
          <h1 className="text-3xl font-bold text-white text-center tracking-wide uppercase" style={{ textShadow: '2px 2px 0px rgba(0,0,0,0.5)' }}>
            {portalName}
          </h1>
          <p className="text-[#39FF14] text-center mt-2 font-medium opacity-90">Self-Service Whitelist Portal</p>
        </div>

        {/* Instructions Area */}
        {instructions && (
          <div className="px-8 pt-8 text-gray-200 text-sm markdown-body">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>{instructions}</ReactMarkdown>
          </div>
        )}

        {/* Form Body */}
        <div className="p-8 pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                Minecraft Username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Notch"
                required
                className="w-full px-4 py-3 bg-black/40 border border-[#7a7a7a] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#4e8036] focus:border-transparent text-white placeholder-gray-500 transition-all duration-300"
              />
            </div>

            {error && (
              <div className="p-4 rounded-lg bg-red-500/20 border border-red-500/50 text-red-200 text-sm animate-pulse">
                {error}
              </div>
            )}

            {message && (
              <div className="p-4 rounded-lg bg-green-500/20 border border-green-500/50 text-green-200 text-sm flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                <span>{message}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 flex justify-center items-center rounded-lg font-bold text-white transition-all duration-300
                ${loading 
                  ? 'bg-[#7a7a7a] cursor-not-allowed' 
                  : 'bg-[#866043] hover:bg-[#6c4c34] active:translate-y-0.5 shadow-[0_4px_0_#4e3624] hover:shadow-[0_2px_0_#4e3624]'
                }`}
            >
              {loading ? (
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                'Add to Whitelist'
              )}
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}

export default App
