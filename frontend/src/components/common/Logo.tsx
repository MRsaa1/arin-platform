'use client'

export default function Logo() {
  return (
    <div className="flex items-center space-x-3">
      {/* SAA Alliance Logo */}
      <div className="flex items-center">
        <span className="text-2xl font-bold text-saa-white tracking-tight">
          SAA
        </span>
        <span className="text-2xl font-bold text-saa-white tracking-tight ml-1">
          Alliance
        </span>
      </div>
      {/* Разделитель */}
      <div className="h-6 w-px bg-saa-border mx-2"></div>
      {/* ARIN подзаголовок */}
      <div className="text-lg font-semibold text-saa-gold">
        ARIN
      </div>
    </div>
  )
}

