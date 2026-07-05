import { useEffect } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

/** Ambient emerald glow that trails the cursor — a subtle premium spotlight. */
export default function CursorGlow() {
  const x = useMotionValue(-500)
  const y = useMotionValue(-500)
  const sx = useSpring(x, { damping: 40, stiffness: 200, mass: 0.6 })
  const sy = useSpring(y, { damping: 40, stiffness: 200, mass: 0.6 })
  const left = useTransform(sx, (v) => v - 300)
  const top = useTransform(sy, (v) => v - 300)

  useEffect(() => {
    const onMove = (e: MouseEvent) => { x.set(e.clientX); y.set(e.clientY) }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [x, y])

  return (
    <motion.div
      aria-hidden
      style={{ left, top }}
      className="pointer-events-none fixed -z-[5] hidden h-[600px] w-[600px] rounded-full bg-emerald-500/[0.07] blur-[100px] lg:block"
    />
  )
}
