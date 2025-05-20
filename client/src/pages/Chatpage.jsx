import { useState } from "react";

import Chat from "../components/Chat";
import Sidebar from "../components/Sidebar";

import { MessageContextProvider } from "../contexts/MessageContext";
export default function Chatpage() {
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    return (
        <div className="w-full">
            <Sidebar
                isDrawerOpen={isDrawerOpen}
                setIsDrawerOpen={setIsDrawerOpen}
            />
            <MessageContextProvider>
                    <Chat
                        isDrawerOpen={isDrawerOpen}
                        setIsDrawerOpen={setIsDrawerOpen}
                    />
            </MessageContextProvider>
        </div>
    );
}
