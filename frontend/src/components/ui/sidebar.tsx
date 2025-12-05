"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Home, User, Settings, Bell, Grid, PanelLeftClose, PanelLeftOpen, Search, Edit, Book, LogOut } from "lucide-react";
import { cn } from "@/src/lib/utils";
import { GalleryIcon } from '@/src/components/ui/gallery-icon';
import { useAuth } from "@/src/context/auth-context";
import { ProfileModal } from "@/src/components/ui/profile-modal";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/src/components/ui/dropdown-menu";

const Sidebar = ({ children }: { children?: React.ReactNode }) => {
    const [isMobileOpen, setIsMobileOpen] = useState(false);
    const [isCollapsed, setIsCollapsed] = useState(false);

    const toggleMobileSidebar = () => setIsMobileOpen(!isMobileOpen);
    const toggleCollapse = () => setIsCollapsed(!isCollapsed);

    const sidebarWidth = isCollapsed ? "w-16" : "w-64";
    const mainContentMargin = isCollapsed ? "md:ml-16" : "md:ml-64";

    return (
        <div className="flex min-h-screen bg-white">
            {/* Mobile Sidebar Overlay */}
            <AnimatePresence>
                {isMobileOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={toggleMobileSidebar}
                        className="md:hidden fixed inset-0 z-40 bg-black/50"
                    />
                )}
            </AnimatePresence>

            {/* Mobile Sidebar */}
            <AnimatePresence>
                {isMobileOpen && (
                    <motion.div
                        initial={{ x: "-100%" }}
                        animate={{ x: 0 }}
                        exit={{ x: "-100%" }}
                        transition={{ type: "spring", bounce: 0, duration: 0.4 }}
                        className="md:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200"
                    >
                        <SidebarContent isCollapsed={false} />
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Desktop Sidebar */}
            <motion.div
                className={cn(
                    "hidden md:flex flex-col fixed inset-y-0 left-0 z-30 bg-white border-r border-gray-200 transition-all duration-300 ease-in-out",
                    sidebarWidth
                )}
            >
                <div className="flex items-center justify-between p-4 h-16 border-b border-gray-100">
                    {!isCollapsed && <span className="font-bold text-lg truncate" style={{ color: '#0f7d70', fontFamily: 'Silver Garden, sans-serif' }}>MugShot Studio</span>}
                    <button
                        onClick={toggleCollapse}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors ml-auto"
                        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                    >
                        {isCollapsed ? <PanelLeftOpen size={20} className="text-black" /> : <PanelLeftClose size={20} className="text-black" />}
                    </button>
                </div>

                <SidebarContent isCollapsed={isCollapsed} />
            </motion.div>

            {/* Main Content */}
            <div className={cn("flex-1 flex flex-col min-h-screen transition-all duration-300 ease-in-out", mainContentMargin)}>
                {/* Mobile Header */}
                <div className="md:hidden flex items-center p-4 border-b border-gray-200 bg-white sticky top-0 z-20">
                    <button onClick={toggleMobileSidebar} className="p-2 -ml-2 hover:bg-gray-100 rounded-lg">
                        <PanelLeftOpen size={24} className="text-black" />
                    </button>
                    <span className="ml-2 font-bold" style={{ color: '#0f7d70', fontFamily: 'Silver Garden, sans-serif' }}>MugShot Studio</span>
                </div>
                <main className="flex-1 relative">
                    {children}
                </main>
            </div>
        </div>
    );
};

const SidebarContent = ({ isCollapsed }: { isCollapsed: boolean }) => {
    const { user, logout } = useAuth();
    const [profileModalOpen, setProfileModalOpen] = useState(false);

    return (
        <div className="flex flex-col h-full py-4">
            <div className="px-3 mb-6 space-y-1">
                <SidebarItem icon={Edit} label="New chat" isCollapsed={isCollapsed} />
                <SidebarItem icon={Search} label="Search chats" isCollapsed={isCollapsed} />
                <SidebarItem icon={GalleryIcon} label="Library" isCollapsed={isCollapsed} />
            </div>

            <div className="flex-1 overflow-y-auto px-3 space-y-1">

            </div>

            {/* Removed Settings from here since it's accessible through the profile section */}
            
            <div className="px-3 mt-auto border-t border-gray-100 pt-4">
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <div className={cn("flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer", isCollapsed && "justify-center")}>
                            <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 shrink-0 overflow-hidden">
                                {user?.profile_photo_url ? (
                                    <img src={user.profile_photo_url} alt="Profile" className="w-full h-full object-cover" />
                                ) : (
                                    <User size={16} />
                                )}
                            </div>
                            {!isCollapsed && (
                                <div className="overflow-hidden text-left">
                                    <p className="text-sm font-medium truncate text-gray-900">{user?.full_name || 'User Account'}</p>
                                    <p className="text-xs text-gray-500 truncate">@{user?.username || 'username'}</p>
                                </div>
                            )}
                        </div>
                    </DropdownMenuTrigger>
                    {/* Updated dropdown menu styling for light mode */}
                    <DropdownMenuContent align="end" className="w-56 bg-white border border-gray-200 text-gray-900" side="top">
                        <DropdownMenuLabel className="text-gray-900">My Account</DropdownMenuLabel>
                        <DropdownMenuSeparator className="bg-gray-200" />
                        <DropdownMenuItem onClick={() => setProfileModalOpen(true)} className="text-gray-700 focus:bg-gray-100 focus:text-gray-900">
                            <User className="mr-2 h-4 w-4" />
                            <span>Profile</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-gray-700 focus:bg-gray-100 focus:text-gray-900">
                            <Settings className="mr-2 h-4 w-4" />
                            <span>Settings</span>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator className="bg-gray-200" />
                        <DropdownMenuItem onClick={logout} className="text-red-600 focus:text-red-600 focus:bg-gray-100">
                            <LogOut className="mr-2 h-4 w-4" />
                            <span>Log out</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>

            <ProfileModal open={profileModalOpen} onOpenChange={setProfileModalOpen} />
        </div>
    );
};

const SidebarItem = ({ icon: Icon, label, isCollapsed, active }: { icon: any, label: string, isCollapsed: boolean, active?: boolean }) => {
    return (
        <button
            className={cn(
                "w-full flex items-center gap-3 p-2 rounded-lg transition-colors group relative",
                active ? "bg-gray-100 text-teal-700" : "text-gray-600 hover:bg-gray-50 hover:text-gray-900",
                isCollapsed && "justify-center"
            )}
            title={isCollapsed ? label : undefined}
        >
            <Icon size={20} className="shrink-0" />
            {!isCollapsed && (
                <span className="text-sm font-medium truncate">{label}</span>
            )}

            {/* Tooltip for collapsed state */}
            {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                    {label}
                </div>
            )}
        </button>
    );
};

export { Sidebar };
