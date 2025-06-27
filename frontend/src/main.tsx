import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'   // 이 줄이 있어야 Tailwind 스타일이 적용됩니다.
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
