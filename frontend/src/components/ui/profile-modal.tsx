'use client';

import React, { useState, useRef } from 'react';
import {
    Modal,
    ModalBody,
    ModalContent,
    ModalHeader,
    ModalTitle,
    ModalDescription
} from '@/src/components/ui/modal';
import { Button } from '@/src/components/ui/button';
import { Input } from '@/src/components/ui/input';
import { useAuth } from '@/src/context/auth-context';
import { authApi } from '@/src/lib/auth';
import { Camera, Loader2, User as UserIcon } from 'lucide-react';
import { Toast } from '@/src/components/ui/toast';

type ProfileModalProps = Omit<React.ComponentProps<typeof Modal>, 'children'>;

export function ProfileModal(props: ProfileModalProps) {
    const { user, refreshProfile, logout } = useAuth();
    const [isLoading, setIsLoading] = useState(false);
    const [displayName, setDisplayName] = useState(user?.full_name || '');
    const [username, setUsername] = useState(user?.username || '');
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Toast State
    const [toastVisible, setToastVisible] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    const showToast = (msg: string) => {
        setToastMessage(msg);
        setToastVisible(true);
    };

    React.useEffect(() => {
        if (user) {
            setDisplayName(user.full_name || '');
            setUsername(user.username || '');
        }
    }, [user]);

    const handleSave = async () => {
        if (!user) return;

        setIsLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error('Not authenticated');

            await authApi.updateProfile(token, {
                full_name: displayName,
                username: username
            });

            await refreshProfile();
            showToast('Profile updated successfully');
            setTimeout(() => props.onOpenChange?.(false), 1000);
        } catch (error: any) {
            showToast(error.message || 'Failed to update profile');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !user) return;

        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            showToast('File size must be less than 5MB');
            return;
        }

        setIsLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error('Not authenticated');

            await authApi.uploadAvatar(token, file);
            await refreshProfile();
            showToast('Profile picture updated');
        } catch (error: any) {
            showToast(error.message || 'Failed to upload avatar');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteAccount = async () => {
        if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) return;

        setIsLoading(true);
        try {
            const token = localStorage.getItem('access_token');
            if (!token) throw new Error('Not authenticated');

            await authApi.deleteAccount(token);
            logout();
            props.onOpenChange?.(false);
        } catch (error: any) {
            showToast(error.message || 'Failed to delete account');
            setIsLoading(false);
        }
    };

    return (
        <Modal {...props}>
            <ModalContent
                className="bg-white text-[#0a3d40] border border-[#e5e5e5] sm:max-w-[425px]"
                popoverProps={{
                    className: "bg-white text-[#0a3d40] border border-[#e5e5e5] sm:max-w-[425px]"
                }}
            >
                <ModalHeader>
                    <ModalTitle className="text-xl font-semibold">Edit profile</ModalTitle>
                    <ModalDescription className="sr-only">
                        Edit your user profile information
                    </ModalDescription>
                </ModalHeader>

                <ModalBody className="py-6">
                    {/* Avatar Section */}
                    <div className="flex justify-center mb-8">
                        <div className="relative group">
                            <div className="w-24 h-24 rounded-full overflow-hidden bg-[#f5f5f5] flex items-center justify-center border-2 border-transparent group-hover:border-[#0f7d70] transition-all">
                                {user?.profile_photo_url ? (
                                    <img
                                        src={user.profile_photo_url}
                                        alt="Profile"
                                        className="w-full h-full object-cover"
                                    />
                                ) : (
                                    <UserIcon className="w-12 h-12 text-[#0a3d40]" />
                                )}
                            </div>
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="absolute bottom-0 right-0 p-2 bg-white rounded-full border border-[#e5e5e5] hover:bg-[#f5f5f5] transition-colors shadow-lg"
                            >
                                <Camera className="w-4 h-4 text-[#0a3d40]" />
                            </button>
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept="image/png, image/jpeg, image/gif"
                                onChange={handleFileChange}
                            />
                        </div>
                    </div>

                    {/* Form Fields */}
                    <div className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[#0a3d40]">Display name</label>
                            <Input
                                value={displayName}
                                onChange={(e) => setDisplayName(e.target.value)}
                                className="bg-white border border-[#e5e5e5] text-[#0a3d40] focus:border-[#0f7d70] focus:ring-0"
                                placeholder="Enter display name"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[#0a3d40]">Username</label>
                            <Input
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="bg-white border border-[#e5e5e5] text-[#0a3d40] focus:border-[#0f7d70] focus:ring-0"
                                placeholder="Enter username"
                            />
                        </div>

                        <p className="text-xs text-[#737373] mt-4">
                            Your profile helps people recognize you. Your name and username are also used in the app.
                        </p>
                    </div>
                </ModalBody>

                <div className="flex justify-between items-center p-6 border-t border-[#e5e5e5]">
                    <button
                        onClick={handleDeleteAccount}
                        className="text-red-500 text-sm hover:underline font-medium"
                    >
                        Delete account
                    </button>

                    <div className="flex gap-3">
                        <Button
                            variant="ghost"
                            onClick={() => props.onOpenChange?.(false)}
                            className="text-[#0a3d40] hover:text-[#0a3d40] hover:bg-[#f5f5f5]"
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleSave}
                            disabled={isLoading}
                            className="bg-[#0f7d70] text-white hover:bg-[#0d6d60] font-medium rounded-full px-6"
                        >
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save'}
                        </Button>
                    </div>
                </div>
            </ModalContent>

            <Toast
                message={toastMessage}
                isVisible={toastVisible}
                onClose={() => setToastVisible(false)}
            />
        </Modal>
    );
}
