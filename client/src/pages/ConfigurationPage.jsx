import { useState, useEffect } from "react";

import { IconButton } from "@material-tailwind/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline"; 

import Sidebar from "../components/Sidebar";
import ConfigGroup from "../components/ConfigGroup";

const SERVER_IP = import.meta.env.VITE_SERVER_IP;

export default function ConfigurationPage() {
    
    const [config, setConfig] = useState([]);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    useEffect(() => {
        // Fetch configuration data from the server
        const fetchConfig = async () => {
            try {
                const response = await fetch(`${SERVER_IP}/api/config`);
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                const data = await response.json();
                console.log("returned data", data);
                setConfig(data);
            } catch (error) {
                console.error("Error fetching configuration:", error);
            }
        };

        fetchConfig();
    }, []);


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
                <div className="p-4 h-full">
                    <h1 className="text-xl font-bold">
                        Configuration
                    </h1>
                    <div className="overflow-y-scroll">
                        {Object.entries(config).map(([group_name, group_content]) => (
                            <ConfigGroup key={group_name} group_name={group_name} group_content={group_content} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
