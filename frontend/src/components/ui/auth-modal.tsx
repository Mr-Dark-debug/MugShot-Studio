'use client';
import React, { useState } from 'react';
import {
    Modal,
    ModalBody,
    ModalContent,
    ModalDescription,
    ModalFooter,
    ModalHeader,
    ModalTitle,
} from '@/src/components/ui/modal';
import Link from 'next/link';
import { Button } from '@/src/components/ui/button';
import { Input } from '@/src/components/ui/input';
import { AtSignIcon, LockIcon, UserIcon, CalendarIcon, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Toast } from '@/src/components/ui/toast';
import { authApi } from '@/src/lib/auth';
import { useAuth } from '@/src/context/auth-context';

type AuthModalProps = Omit<React.ComponentProps<typeof Modal>, 'children'>;

type AuthStep = 'email' | 'signin' | 'signup';

export function AuthModal(props: AuthModalProps) {
    const router = useRouter();
    const { login } = useAuth();
    const [step, setStep] = useState<AuthStep>('email');
    const [isLoading, setIsLoading] = useState(false);

    // Form States
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [username, setUsername] = useState('');
    const [fullName, setFullName] = useState('');
    const [dob, setDob] = useState('');

    // Toast State
    const [toastVisible, setToastVisible] = useState(false);
    const [toastMessage, setToastMessage] = useState('');

    const showToast = (msg: string) => {
        setToastMessage(msg);
        setToastVisible(true);
    };

    const hideToast = () => {
        setToastVisible(false);
    };

    const handleEmailSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!email) return showToast('Please enter your email');

        setIsLoading(true);
        try {
            const res = await authApi.start(email);
            if (res.exists) {
                setStep('signin');
            } else {
                setStep('signup');
            }
        } catch (error: any) {
            showToast(error.message || 'Something went wrong');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSignin = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!password) return showToast('Please enter your password');

        setIsLoading(true);
        try {
            const res = await authApi.signin({ email, password });
            login(res.access_token, res.user);
            showToast('Successfully signed in!');
            setTimeout(() => {
                props.onOpenChange?.(false);
                router.push('/chat');
            }, 1000);
        } catch (error: any) {
            showToast(error.message || 'Invalid credentials');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSignup = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!password || !confirmPassword || !username || !fullName || !dob) {
            return showToast('Please fill in all fields');
        }
        if (password !== confirmPassword) {
            return showToast('Passwords do not match');
        }

        setIsLoading(true);
        try {
            const res = await authApi.signup({
                email,
                password,
                confirm_password: confirmPassword,
                username,
                full_name: fullName,
                dob
            });
            login(res.access_token, res.user);
            showToast('Account created successfully!');
            setTimeout(() => {
                props.onOpenChange?.(false);
                router.push('/chat');
            }, 1000);
        } catch (error: any) {
            showToast(error.message || 'Signup failed');
        } finally {
            setIsLoading(false);
        }
    };

    const resetFlow = () => {
        setStep('email');
        setEmail('');
        setPassword('');
        setConfirmPassword('');
        setUsername('');
        setFullName('');
        setDob('');
    };

    // Reset flow when modal closes
    React.useEffect(() => {
        if (!props.open) {
            setTimeout(resetFlow, 300);
        }
    }, [props.open]);

    return (
        <Modal {...props}>
            <ModalContent
                popoverProps={{
                    className: "bg-white border border-[#0f7d70] shadow-xl data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=open]:slide-in-from-bottom-2 data-[state=open]:slide-in-from-left-1/2 duration-300 rounded-xl max-h-[90vh] overflow-y-auto"
                }}
                drawerProps={{
                    className: "bg-white border border-[#0f7d70] shadow-xl rounded-t-xl max-h-[90vh] overflow-y-auto"
                }}
            >
                <ModalHeader
                    className="rounded-t-xl"
                    drawerProps={{
                        className: "rounded-t-xl border-b border-[#0f7d70]"
                    }}
                >
                    <ModalTitle
                        className="text-center text-2xl font-semibold text-[#0f7d70] py-4"
                        drawerProps={{
                            className: "text-center text-2xl font-semibold text-[#0f7d70] py-4"
                        }}
                    >
                        {step === 'email' && 'Sign In or Join Now!'}
                        {step === 'signin' && 'Welcome Back!'}
                        {step === 'signup' && 'Create Your Account'}
                    </ModalTitle>
                    <ModalDescription className="sr-only">
                        Authentication modal
                    </ModalDescription>
                </ModalHeader>
                <ModalBody>
                    {step === 'email' && (
                        <form onSubmit={handleEmailSubmit} className="space-y-4">
                            <Button
                                type="button"
                                variant="outline"
                                className="w-full duration-300 border-2 border-[#0f7d70] hover:bg-[#0f7d70] group h-12 rounded-lg"
                                onClick={() => showToast('Google login coming soon!')}
                            >
                                <GoogleIcon className="w-5 h-5 me-2 group-hover:text-white" />
                                <span className="group-hover:text-white font-medium">Continue With Google</span>
                            </Button>

                            <div className="relative my-6">
                                <div className="absolute inset-0 flex items-center">
                                    <span className="w-full border-t border-[#0f7d70]/30" />
                                </div>
                                <div className="relative flex justify-center text-xs uppercase">
                                    <span className="bg-white text-[#0f7d70] px-4 font-bold">
                                        OR
                                    </span>
                                </div>
                            </div>

                            <div className="relative h-max">
                                <Input
                                    placeholder="your.email@example.com"
                                    className="peer ps-9 h-12 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    autoFocus
                                />
                                <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                    <AtSignIcon className="size-5" aria-hidden="true" />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full duration-300 bg-[#0f7d70] hover:bg-[#0c6a61] text-white h-12 rounded-lg font-medium"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : 'Continue'}
                            </Button>
                        </form>
                    )}

                    {step === 'signin' && (
                        <form onSubmit={handleSignin} className="space-y-4">
                            <div className="text-sm text-center text-gray-600 mb-4">
                                Signing in as <span className="font-semibold text-[#0f7d70]">{email}</span>
                                <button type="button" onClick={() => setStep('email')} className="ml-2 text-xs text-blue-500 hover:underline">Change</button>
                            </div>

                            <div className="relative h-max">
                                <Input
                                    placeholder="Password"
                                    className="peer ps-9 h-12 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    autoFocus
                                />
                                <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                    <LockIcon className="size-5" aria-hidden="true" />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full duration-300 bg-[#0f7d70] hover:bg-[#0c6a61] text-white h-12 rounded-lg font-medium"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : 'Sign In'}
                            </Button>

                            <div className="text-center">
                                <button type="button" className="text-xs text-[#0f7d70] hover:underline">
                                    Forgot Password?
                                </button>
                            </div>
                        </form>
                    )}

                    {step === 'signup' && (
                        <form onSubmit={handleSignup} className="space-y-3">
                            <div className="text-sm text-center text-gray-600 mb-2">
                                Creating account for <span className="font-semibold text-[#0f7d70]">{email}</span>
                                <button type="button" onClick={() => setStep('email')} className="ml-2 text-xs text-blue-500 hover:underline">Change</button>
                            </div>

                            <div className="grid grid-cols-2 gap-3">
                                <div className="relative h-max">
                                    <Input
                                        placeholder="Username"
                                        className="peer ps-9 h-10 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                    />
                                    <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                        <UserIcon className="size-4" aria-hidden="true" />
                                    </div>
                                </div>
                                <div className="relative h-max">
                                    <Input
                                        placeholder="Full Name"
                                        className="peer ps-9 h-10 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                        value={fullName}
                                        onChange={(e) => setFullName(e.target.value)}
                                    />
                                    <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                        <UserIcon className="size-4" aria-hidden="true" />
                                    </div>
                                </div>
                            </div>

                            <div className="relative h-max">
                                <Input
                                    placeholder="Date of Birth"
                                    type="date"
                                    className="peer ps-9 h-10 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                    value={dob}
                                    onChange={(e) => setDob(e.target.value)}
                                />
                                <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                    <CalendarIcon className="size-4" aria-hidden="true" />
                                </div>
                            </div>

                            <div className="relative h-max">
                                <Input
                                    placeholder="Password"
                                    type="password"
                                    className="peer ps-9 h-10 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                                <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                    <LockIcon className="size-4" aria-hidden="true" />
                                </div>
                            </div>

                            <div className="relative h-max">
                                <Input
                                    placeholder="Confirm Password"
                                    type="password"
                                    className="peer ps-9 h-10 border-2 border-[#0f7d70]/30 focus:border-[#0f7d70] focus:ring-2 focus:ring-[#0f7d70]/20 rounded-lg text-[#0f7d70] bg-white"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                />
                                <div className="text-[#0f7d70] pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 peer-disabled:opacity-50">
                                    <LockIcon className="size-4" aria-hidden="true" />
                                </div>
                            </div>

                            <Button
                                type="submit"
                                disabled={isLoading}
                                className="w-full duration-300 bg-[#0f7d70] hover:bg-[#0c6a61] text-white h-12 rounded-lg font-medium"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : 'Create Account'}
                            </Button>
                        </form>
                    )}
                </ModalBody>
                <ModalFooter
                    className="p-4 rounded-b-xl"
                    drawerProps={{
                        className: "p-4 rounded-b-xl border-t border-[#0f7d70]"
                    }}
                >
                    <p className="text-[#0f7d70] text-center text-xs">
                        By clicking Continue, you agree to our{' '}
                        <Link className="text-[#0f7d70] hover:underline font-bold" href="/policy">
                            Privacy Policy
                        </Link>
                        .
                    </p>
                </ModalFooter>
            </ModalContent>
            <Toast
                message={toastMessage}
                isVisible={toastVisible}
                onClose={hideToast}
            />
        </Modal>
    );
}

const GoogleIcon = (props: React.ComponentProps<'svg'>) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        fill="currentColor"
        {...props}
    >
        <g>
            <path d="M12.479,14.265v-3.279h11.049c0.108,0.571,0.164,1.247,0.164,1.979c0,2.46-0.672,5.502-2.84,7.669   C18.744,22.829,16.051,24,12.483,24C5.869,24,0.308,18.613,0.308,12S5.869,0,12.483,0c3.659,0,6.265,1.436,8.223,3.307L18.392,5.62   c-1.404-1.317-3.307-2.341-5.913-2.341C7.65,3.279,3.873,7.171,3.873,12s3.777,8.721,8.606,8.721c3.132,0,4.916-1.258,6.059-2.401   c0.927-0.927,1.537-2.251,1.777-4.059L12.479,14.265z" />
        </g>
    </svg>
);