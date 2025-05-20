import { useContext } from "react";

import { PlusIcon, TrashIcon } from "@heroicons/react/24/outline";

import { fetchData } from "../utils/fetchData";
import { WorkspaceContext } from "../contexts/WorkspaceContext";
import { UserContext } from "../contexts/UserContext";

function WorkspaceListItem({ workspace }) {
    const { userId } = useContext(UserContext);

    const handleDeleteWorkspace = () => {
        // confirm
        const confirmDelete = window.confirm(
            `Are you sure you want to delete the workspace ${workspace.name}?`
        );
        if (!confirmDelete) {
            return;
        }
        // Call the API to delete the workspace
        try {
            const data = fetchData(
                `workspace/${userId}/${workspace.id}`,
                "DELETE"
            ).then((response) => {
                console.log("Delete workspace success, response:", response);
                // reload the page
                window.location.reload();
            });
        } catch (error) {
            console.error("Error deleting workspace:", error);
        }
    };

    return (
        <div className="my-1 flex justify-between">
            <div>{workspace.name}</div>
            <div>
                <TrashIcon
                    title="Delete workspace "
                    onClick={handleDeleteWorkspace}
                    className="h-5 w-5 hover:cursor-pointer"
                />
            </div>
        </div>
    );
}

function WorkspaceList() {
    const { workspaces } = useContext(WorkspaceContext);
    return (
        <div className="m-2">
            {workspaces.map((workspace) => (
                <WorkspaceListItem key={workspace.id} workspace={workspace} />
            ))}
        </div>
    );
}

export default function WorkspaceManagement() {
    const { userId } = useContext(UserContext);
    const { workspaces } = useContext(WorkspaceContext);

    const handleCreateWorkspace = async () => {
        // prompt user to ender workspace new id
        const newWorkspaceName = prompt("Enter new workspace name:");
        // cheeck workspace id not in current workspace list
        if (newWorkspaceName && newWorkspaceName.trim() === "") {
            alert("Workspace ID cannot be empty.");
            return;
        }
        
        if (
            newWorkspaceName &&
            workspaces.some((workspace) => workspace.name === newWorkspaceName)
        ) {
            alert("Workspace Name already exists.");
            return;
        }
        if (newWorkspaceName) {
            // Call the API to create a new workspace
            try {
                const data = await fetchData(
                    `workspace/${userId}/${newWorkspaceName}`,
                    "POST"
                );
                console.log("Created workspace:", data);

                // Update the workspace list in the context
                // reload the page
                window.location.reload();
            } catch (error) {
                console.error("Error creating workspace:", error);
            }
        }
    };

    return (
        <div>
            {/* Create Workspace */}
            <div className="flex justify-between items-center">
                <h1 className="text-xl font-bold mt-2 py-2">Workspaces</h1>
                {/* Create Worksapce */}
                <div
                    className="flex items-center gap-1 rounded-sm bg-gray-700 py-1 px-3 hover:cursor-pointer"
                    onClick={handleCreateWorkspace}
                >
                    <PlusIcon
                        className="h-5 w-5 stroke-2 text-white"
                        title="Create Workspace"
                    />
                    Workspace
                </div>
            </div>
            {/* Workspace List */}
            <WorkspaceList />
        </div>
    );
}
