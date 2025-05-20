import { useEffect, useContext, useState } from "react";

import { fetchData } from "./fetchData";
import { UserContext } from "../contexts/UserContext";
import { WorkspaceContext } from "../contexts/WorkspaceContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";

// fetch user_ids, and workspaces of the user
// and set the current workspace
export default function useFetchUserData() {
    const { setUserId } = useContext(UserContext);
    const { setWorkspaces } = useContext(WorkspaceContext);
    const { currentWorkspace, setCurrentWorkspace } = useContext(
        CurrentWorkspaceContext
    );

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            try {
                // 1. get user id using getData and set user id
                console.log("Fetching user id...");
                const fetchedUserId = await fetchData("user", "GET");
                setUserId(fetchedUserId);

                // 2. use userid to get workspace id wiht getData (another call)
                const fetchedWorkspaceData = await fetchData(
                    `workspaces/${fetchedUserId}`,
                    "GET"
                );

                // 3. set workspace ids and current workspace id
                setWorkspaces(fetchedWorkspaceData);

                if (
                    !currentWorkspace ||
                    !fetchedWorkspaceData.includes(currentWorkspace)
                ) {
                    setCurrentWorkspace(fetchedWorkspaceData[0]);
                }
                setLoading(false);
            } catch (error) {
                console.error("Error fetching user data:", error);
                setError(error);
                setLoading(false);
            }
        };
        loadData();
    }, []);

    return { loading, error };
}
