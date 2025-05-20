import NewsCard from "./News";

function Message({ message }) {
    return (
        <div className="px-2">
            <div className="lg:max-w-[90%] mx-auto">
                {/* Message bubble */}
                <div
                    className={`rounded-lg shadow-md p-3  ${
                        message.sender === "User"
                            ? "bg-gray-700 ml-auto text-white max-w-[90%]"
                            : "text-gray-200"
                    }`}
                >
                    {message.quoting && (
                        <div className="items-center pb-1">
                            <div className="text-xs text-gray-400 font-semibold pr-2">
                                Quoting News
                            </div>
                            <a href={message.quoting.link} target="_blank">
                                <div className="text-xs text-gray-300">
                                    {message.quoting.title}
                                </div>
                            </a>
                        </div>
                    )}
                    <div className="">{message.content}</div>
                    {message.news.length > 0 && (
                        <div className="mt-2 space-y-2">
                            {message.news.map((news, index) => (
                                <NewsCard key={index} news={news} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function ChatRecord({ messages }) {
    return (
        <div className="flex-1 overflow-y-auto bg-gray-800 p-4 max-h-[90%]">
            {messages.map((message, index) => (
                <Message key={index} message={message} />
            ))}
        </div>
    );
}

export default ChatRecord;
