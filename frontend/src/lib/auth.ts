const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export interface User {
    id: string;
    email: string;
    username: string;
    full_name?: string;
    dob?: string;
    profile_photo_url?: string;
    plan: string;
    credits: number;
    created_at: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
}

export interface AuthStartResponse {
    exists: boolean;
    next: 'password' | 'social_login' | 'create_account';
}

export const authApi = {
    async start(email: string): Promise<AuthStartResponse> {
        const res = await fetch(`${API_URL}/api/v1/auth/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email }),
        });
        if (!res.ok) throw new Error('Failed to check user');
        return res.json();
    },

    async signup(data: any): Promise<AuthResponse> {
        const res = await fetch(`${API_URL}/api/v1/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Signup failed');
        }
        return res.json();
    },

    async signin(data: any): Promise<AuthResponse> {
        const res = await fetch(`${API_URL}/api/v1/auth/signin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.detail || 'Signin failed');
        }
        return res.json();
    },

    async getProfile(token: string): Promise<User> {
        const res = await fetch(`${API_URL}/api/v1/profile/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
        });
        if (!res.ok) throw new Error('Failed to fetch profile');
        return res.json();
    }
};
