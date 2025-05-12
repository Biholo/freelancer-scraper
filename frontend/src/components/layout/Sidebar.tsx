"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  LayoutGrid,
  BarChart2,
  Users,
  MessageCircle,
  Bookmark,
  Bell,
  HelpCircle,
  Settings,
  ChevronLeft,
  Rocket,
  BarChart,
  UserCheck
} from "lucide-react"
import type React from "react"
import { Link, useLocation } from "react-router-dom"

interface SidebarItem {
  icon: React.ReactNode
  label: string
  href: string
}

export default function Sidebar() {
  const [isExpanded, setIsExpanded] = useState(true)
  const location = useLocation()

  const menuItems: SidebarItem[] = [
    { icon: <BarChart size={20} />, label: "Analytics Dashboard", href: "/dashboard" },
    { icon: <Users size={20} />, label: "Freelancers", href: "/freelancers" },
  ]

  return (
    <motion.div
      animate={{ width: isExpanded ? "240px" : "70px" }}
      transition={{ duration: 0.3 }}
      className="min-h-screen relative bg-gradient-to-b from-[#0A0A29] to-[#0A0A1F] text-white p-4 flex flex-col flex-shrink-0"
    >
      {/* Toggle Button */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="absolute -right-3 top-8 bg-blue-600 p-1.5 rounded-full text-white hover:bg-blue-700 transition-colors z-10"
      >
        <motion.div animate={{ rotate: isExpanded ? 0 : 180 }} transition={{ duration: 0.3 }}>
          <ChevronLeft size={16} />
        </motion.div>
      </button>

      {/* Profile Section */}
      <div className="flex items-center gap-4 mb-8">
        <div className="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 bg-blue-600 flex items-center justify-center">
          <UserCheck size={18} />
        </div>
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col"
            >
              <div className="flex items-center gap-1">
                <span className="font-semibold">Freelancer Analytics</span>
              </div>
              <span className="text-sm text-gray-300">Admin Dashboard</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation Items */}
      <nav className="space-y-2 flex-1">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.href
          
          return (
            <Link
              key={item.label}
              to={item.href}
              className={`flex items-center gap-4 ${
                isActive 
                  ? "text-white bg-blue-600" 
                  : "text-gray-300 hover:text-white hover:bg-white/10"
              } rounded-lg p-2 transition-colors group`}
            >
              <span className={`flex-shrink-0 ${isActive ? "text-white" : "group-hover:text-blue-400"} transition-colors`}>
                {item.icon}
              </span>
              <AnimatePresence>
                {isExpanded && (
                  <motion.span
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="text-sm whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          )
        })}
      </nav>
    </motion.div>
  )
}

