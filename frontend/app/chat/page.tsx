import GradientBackground from "@/src/components/ui/gradient-background";
import { Sidebar } from "@/src/components/ui/sidebar";

export default function ChatPage() {
    return (
        <Sidebar>
            <GradientBackground>
                <div className="flex items-center justify-center min-h-screen">
                    <h1 className="text-4xl font-bold text-[#0f7d70]">Chat Page</h1>
                </div>
            </GradientBackground>
        </Sidebar>
    );
}
