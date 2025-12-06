'use client'

import Link from 'next/link'
import Logo from './Logo'

export default function Header() {
  return (
    <header className="bg-saa-darker border-b border-saa-border">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo - SAA Alliance стиль */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="group">
              <Logo />
            </Link>
            <div className="hidden lg:block text-xs text-saa-white/60 ml-4 font-light">
              Autonomous Risk Intelligence Network
            </div>
          </div>

          {/* Actions - как на saa-alliance.com */}
          <div className="flex items-center space-x-4">
            <button className="text-saa-white hover:text-saa-gold transition-colors text-sm font-medium">
              Sign in
            </button>
            <button className="bg-saa-darker border border-saa-border text-saa-white hover:border-saa-gold hover:text-saa-gold transition-colors px-4 py-2 rounded text-sm font-medium">
              Get Access
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

