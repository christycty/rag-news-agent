import { useState, useEffect, useContext } from "react";

import { fetchData } from "./fetchData";
import { UserContext } from "../contexts/UserContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";

// Utility function to transform API response into chat message format
const transformDailyNewsToMessage = (dailyNews) => ({
    index: 0,
    sender: "Bot",
    content: dailyNews.summary,
    news: dailyNews.articles.map((article) => ({
        id: article.id,
        title: article.metadata.title,
        summary: article.page_content,
        link: article.metadata.url,
        timestamp: article.metadata.publish_date,
        tags: article.metadata.tags,
        bookmarked: article.bookmarked,
    })),
});

function useFetchDailyNews() {
    const { userId } = useContext(UserContext);
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);
    

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [dailyNewsMessage, setDailyNewsMessage] = useState(null);

    useEffect(() => {
        const fetchDailyNews = async () => {
            setLoading(true);
            try {
                const dailyNews = await fetchData(
                    `daily_news/${userId}/${currentWorkspace.id}`,
                    "GET"
                );
                const message = transformDailyNewsToMessage(dailyNews);
                setDailyNewsMessage(message);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchDailyNews();
    }, [userId, currentWorkspace]); 

    return { loading, error, dailyNewsMessage };
}

export { useFetchDailyNews };