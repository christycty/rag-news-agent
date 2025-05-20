// TODO: put all fetch api calls here in same function
const SERVER_IP = import.meta.env.VITE_SERVER_IP;

async function fetchData(url, method) {
    try {
        const full_url = new URL(`${SERVER_IP}/api/${url}`);
        console.log("fetchData URL:", full_url);
        const response = await fetch(full_url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
        });
        const data = await response.json();
        console.log("fetchData Success:", data);
        return data;
    } catch (error) {
        console.error("fetchData Error:", error);
        throw error;
    }
}


async function fetchDataWithBody(url, method, body) {
    try {
        const full_url = new URL(`${SERVER_IP}/api/${url}`);
        const response = await fetch(full_url, {
            method: method,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        console.log("fetchDataWithBody Success:", data);
        return data;
    } catch (error) {
        console.error("fetchDataWithBody Error:", error);
        throw error;
    }
}


export { fetchData, fetchDataWithBody };
