import { useContext, useEffect, useState } from "react";

import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/outline";

import { fetchData } from "../utils/fetchData";
import { UserContext } from "../contexts/UserContext";
import { WorkspaceContext } from "../contexts/WorkspaceContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";

function WorkspaceDisplayDropdown({
    workspaceOnDisplay,
    setWorkspaceOnDisplay,
}) {
    const { workspaces } = useContext(WorkspaceContext);

    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const handleDropdownToggle = () => {
        setIsDropdownOpen(!isDropdownOpen);
    };
    const handleWorkspaceSelect = (workspace) => {
        setWorkspaceOnDisplay(workspace);
        setIsDropdownOpen(false);
    };

    return (
        <div className="">
            <div
                className="bg-gray-800 text-white flex justify-between items-center gap-10 py-1 px-2 border-1 border-gray-500 rounded-sm"
                onClick={handleDropdownToggle}
            >
                {workspaceOnDisplay.name}
                <ChevronDownIcon className="w-5 h-5" />
            </div>
            {isDropdownOpen && (
                <div className="absolute bg-gray-800 text-white border-1 border-gray-500">
                    {workspaces.map((workspace) => (
                        <div
                            key={workspace.id}
                            className={`p-2 text-sm hover:bg-gray-600 cursor-pointer  ${
                                workspaceOnDisplay.id === workspace.id
                                    ? "font-semibold bg-gray-700"
                                    : ""
                            }`}
                            onClick={() => handleWorkspaceSelect(workspace)}
                        >
                            {workspace.name}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default function InterestProfile() {
    const { userId } = useContext(UserContext);
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);

    const [workspaceOnDisplay, setWorkspaceOnDisplay] =
        useState(currentWorkspace);
    const [workspaceInterests, setWorkspaceInterests] = useState([]);

    useEffect(() => {
        const fetchWorkspaceInterests = async (workspace) => {
            // fetch using getData
            return fetchData(`interests/${userId}/${workspace.id}`, "GET");
        };

        fetchWorkspaceInterests(workspaceOnDisplay)
            .then((data) => {
                console.log("Fetched interests:", data);
                setWorkspaceInterests(data);
            })
            .catch((error) => {
                console.error("Error fetching interests:", error);
            });
    }, [workspaceOnDisplay]);

    return (
        <div>
            <div className="flex justify-between  items-center">
                <h1 className="text-xl font-bold mt-2 py-2">
                    Interest Profiles
                </h1>
                <WorkspaceDisplayDropdown
                    workspaceOnDisplay={workspaceOnDisplay}
                    setWorkspaceOnDisplay={setWorkspaceOnDisplay}
                />
            </div>

            {/* Content: Tag of display workspace */}
            <div className="mt-2">
                {/* display the array */}
                <ul className="m-2">
                    {workspaceInterests.map((interest) => (
                        <li className="my-1" key={interest}>
                            {interest}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
