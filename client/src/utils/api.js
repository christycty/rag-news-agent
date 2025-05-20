
const SERVER_IP = import.meta.env.VITE_SERVER_IP;

// Bookmark
const fetchAllBookmarks = async () => {
    try {
        const url = new URL(`${SERVER_IP}/api/bookmarks`);
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        console.log("Success:", data);
        return data;
    } catch (error) {
        console.error("Error:", error);
        throw error;
    }
};

const deleteBookmark = async (id) => {
    try {
        const url = new URL(`${SERVER_IP}/api/bookmark/${id}`);
        const response = await fetch(url, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        console.log("Success:", data);
        return data;
    }
    catch (error) {
            console.error("Error:", error);
            throw error;
        }
};


// Workspace API
const fetchWorkspaceId = async (userId) => {
    try {
        const url = new URL(`${SERVER_IP}/api/workspaces/${userId}`);
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        console.log("Success:", data);
        return data;
    } catch (error) {
        console.error("Error:", error);
        throw error;
    }
}


export {fetchAllBookmarks, deleteBookmark, fetchWorkspaceId};