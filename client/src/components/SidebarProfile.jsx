import { useContext, useState } from "react";

import {
    UserCircleIcon,
    ChevronDownIcon,
    ChevronUpIcon,
} from "@heroicons/react/24/solid";

import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";
import { WorkspaceContext } from "../contexts/WorkspaceContext";
import { UserContext } from "../contexts/UserContext";


function WorkspaceMenu() {
    const { currentWorkspace, setCurrentWorkspace } = useContext(
        CurrentWorkspaceContext
    );
    const { workspaces } = useContext(WorkspaceContext);

    const handleWorkspaceClick = (workspace) => {
        setCurrentWorkspace(workspace);
    };

    return (
        <div className="ml-9 mb-1 text-white border-white border-x-1 border-t-1">
            {workspaces.map((workspace) => (
                <div
                    key={workspace.id}
                    className={`p-2 text-sm hover:bg-gray-600 cursor-pointer  ${
                        currentWorkspace === workspace
                            ? "font-semibold bg-gray-700"
                            : ""
                    }`}
                    onClick={() => handleWorkspaceClick(workspace)}
                >
                    {workspace.name}
                </div>
            ))}
        </div>
    );
}

export default function SidebarProfile() {
    const { userId } = useContext(UserContext);
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);

    const [isWorkspaceMenuOpen, setIsWorkspaceMenuOpen] = useState(false);

    const handleWorkspaceClick = () => {
        setIsWorkspaceMenuOpen(!isWorkspaceMenuOpen);
    };

    return (
        <div>
            <div>{isWorkspaceMenuOpen && <WorkspaceMenu />}</div>
            <div className="mt-auto flex gap-3 text-white mb-2">
                {/* User Icon */}
                <div className="items-baseline h-full pt-1">
                    <UserCircleIcon className="h-8 w-8" />
                </div>
                <div className="w-full pr-2">
                    <div className="text-gray-400 text-xs font-semibold">
                        {userId}
                    </div>
                    <div className="flex justify-between w-full">
                        <div className="text-sm">{currentWorkspace.name}</div>
                        <div>
                            {isWorkspaceMenuOpen ? (
                                <ChevronUpIcon
                                    className="pt-1 h-4 w-4 hover:cursor-pointer"
                                    onClick={handleWorkspaceClick}
                                />
                            ) : (
                                <ChevronDownIcon
                                    className="pt-1 h-4 w-4 hover:cursor-pointer"
                                    onClick={handleWorkspaceClick}
                                />
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
