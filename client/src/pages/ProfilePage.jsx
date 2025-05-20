import { useState } from "react";

import { IconButton } from "@material-tailwind/react";
import {
    Bars3Icon,
    XMarkIcon,
} from "@heroicons/react/24/outline";

import Sidebar from "../components/Sidebar";
import InterestProfile from "../components/InterestProfile";
import WorkspaceManagement from "../components/Workspace";

export default function ProfilePage() {
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const openDrawer = () => setIsDrawerOpen(true);
    
    return (
        <div className="flex w-full">
            <Sidebar
                isDrawerOpen={isDrawerOpen}
                setIsDrawerOpen={setIsDrawerOpen}
            />
            <div className="bg-gray-800 text-white h-screen w-full flex-col flex">
                {/* Hamburger icon for sidebar */}
                <IconButton
                    size="lg"
                    onClick={openDrawer}
                    className="hover:cursor-pointer bg-transparent"
                >
                    {isDrawerOpen ? (
                        <XMarkIcon className="h-8 w-8 stroke-2" />
                    ) : (
                        <Bars3Icon className="h-8 w-8 stroke-2 text-white" />
                    )}
                </IconButton>
                <div className="mx-6">
                    <WorkspaceManagement />
                    <InterestProfile />
                </div>
            </div>
        </div>
    );
}
