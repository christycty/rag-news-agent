import { useState, useEffect, useContext, useMemo } from "react";
import {
    PaperAirplaneIcon,
    XMarkIcon,
    Bars3Icon,
    ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { Button, IconButton, Input } from "@material-tailwind/react";

import ChatRecord from "./ChatRecord";
import { fetchDataWithBody } from "../utils/fetchData";
import { useFetchDailyNews } from "../utils/useFetchDailyNews";

import { MessageContext } from "../contexts/MessageContext";
import { QuoteContext } from "../contexts/QuoteContext";
import { UserContext } from "../contexts/UserContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";


function Chatbar({ handleSubmit, handleReset }) {
    const { quote, setQuote } = useContext(QuoteContext);
    const { message, setMessage } = useContext(MessageContext);

    const handleCancelMention = () => {
        // set quote as null
        setQuote('');
    };

    return (
        <div className="fixed bottom-0 left-0 right-0 m-3">
            {quote && (
                <div className="items-center bg-gray-900 mb-2 rounded-lg pt-2 pb-3 px-3">
                    <div className="flex justify-between my-1">
                        <div className="text-gray-400 text-xs">
                            Quoting News
                        </div>
                        <XMarkIcon
                            className="h-4 w-4 stroke-2 text-gray-400 cursor-pointer"
                            onClick={handleCancelMention}
                        />
                    </div>
                    <div className="font-semibold text-sm">{quote.title}</div>
                </div>
            )}
            <form
                onSubmit={handleSubmit}
                className="flex items-center gap-2 bg-gray-700 rounded-lg px-2"
            >
                <Button
                    onClick={handleReset}
                    className="rounded-full pl-1 hover:cursor-pointer shadow-none bg-transparent flex items-center justify-center"
                    size="sm"
                >
                    <ArrowPathIcon className="h-5 w-5 stroke-2 text-white" />
                </Button>

                {/* Input field */}
                <Input
                    variant="standard"
                    color="white"
                    placeholder="Type your message here..."
                    size="md"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none !border-b-0 pt-0 pb-3 mt-0 mb-1"
                    containerProps={{
                        className: "flex items-center h-full",
                    }}
                    labelProps={{
                        className: "hidden",
                    }}
                />

                {/* Send button */}
                <Button
                    type="submit"
                    className="rounded-full p-2 shadow-none hover:cursor-pointer bg-transparent flex items-center justify-center"
                    size="sm"
                >
                    <PaperAirplaneIcon className="h-5 w-5 stroke-2 text-white" />
                </Button>
            </form>
        </div>
    );
}

// send user query to server
async function sendRequest(message, context, quote, user, workspace_id, newsIds) {
    try {
        const body = {
            query: message,
            context: context,
            quote: quote.title,
            user_id: user,
            workspace_id: workspace_id,
            news_ids: newsIds,
        };
        console.log("sending body", body);

        const data = await fetchDataWithBody("query", "POST", body)

        // map data to news
        const news = data.articles.map((article) => ({
            id: article.id,
            title: article.metadata.title,
            summary: article.page_content,
            link: article.metadata.url,
            timestamp: article.metadata.publish_date,
            tags: article.metadata.tags,
            bookmarked: article.bookmarked,
        }));

        const reply = {
            message: data.summary,
            news: news,
        };

        return reply;
    } catch (error) {
        console.error("Error sending request:", error);
        return null;
    }
}

function Chat({ isDrawerOpen, setIsDrawerOpen }) {
    const { userId } = useContext(UserContext);
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);
    const { quote, setQuote } = useContext(QuoteContext);
    const { message, setMessage } = useContext(MessageContext);

    const [chatRecord, setChatRecord] = useState([]);

    const { loading, error, dailyNewsMessage } = useFetchDailyNews();

    const newsIds = useMemo(() => {
        return chatRecord
          .filter((message) => message.sender === 'Bot')
          .flatMap((message) => message.news.map((newsItem) => newsItem.id));
      }, [chatRecord]);

    useEffect(() => {
        // clear chat record on workspace change
        if (currentWorkspace) {
            setChatRecord([]);
        }
        if (dailyNewsMessage) {
          setChatRecord((prev) => {
            // Avoid duplicate messages (e.g., check if already exists)
            if (prev.some((msg) => msg.index === dailyNewsMessage.index)) {
              return prev;
            }
            return [...prev, dailyNewsMessage];
          });
        }
      }, [dailyNewsMessage, currentWorkspace, setChatRecord]);

    
    const openDrawer = () => setIsDrawerOpen(true);
    
    const handleReset = () => {
        // clear chat record
        setChatRecord([]);
        // clear quote and message
        setQuote("");
        setMessage("");
    };
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (message.trim()) {
            // Handle message submission here
            console.log("Sending message:", message);

            // add message to messages
            const newUserMessage = {
                index: chatRecord.length + 1,
                sender: "User",
                content: message.trim(),
                news: [],
            };
            if (quote) {
                newUserMessage.quoting = quote;
            }
            setChatRecord((prev) => [...prev, newUserMessage]);

            // reset input
            setMessage("");
            setQuote("");

            // send request to server
            try {
                // Send request to server and wait for response
                const context = chatRecord
                    .filter((msg) => msg.sender === "User")
                    .map((msg) => msg.content)
                    .join("\n");

                const serverResponse = await sendRequest(message, context, quote, userId, currentWorkspace.id, newsIds);

                // add a loading message
                const loadingMessage = {
                    index: chatRecord.length + 2,
                    sender: "Bot",
                    content: "Loading...",
                    news: [],
                };
                setChatRecord((prev) => [...prev, loadingMessage]);

                // Add server response to chat record if it exists
                if (serverResponse) {
                    // remove loading message
                    setChatRecord((prev) =>
                        prev.filter((msg) => msg.index !== loadingMessage.index)
                    );

                    const botMessage = {
                        index: chatRecord.length + 2,
                        sender: "Bot",
                        content:
                            serverResponse.message ||
                            "Sorry, I didn't understand that.",
                        news: serverResponse.news || [],
                    };
                    setChatRecord((prev) => [...prev, botMessage]);
                }
            } catch (error) {
                console.error("Failed to get server response:", error);
            }
        }
    };

    return (
        <>
            <div className="border-0 border-green-500 bg-gray-800 text-white h-screen w-full flex flex-col">
                {/* Sidebar button */}
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

                {/* Chat record */}
                <div className="flex-1 overflow-y-auto">
                    <ChatRecord messages={chatRecord} />
                </div>

                {/* Chatbar for user input */}
                <Chatbar
                    handleSubmit={handleSubmit}
                    handleReset={handleReset}
                />
            </div>
        </>
    );
}

export default Chat;
