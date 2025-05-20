import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { ChevronDownIcon, ChevronUpIcon } from "@heroicons/react/24/solid";

import { TrashIcon, AtSymbolIcon } from "@heroicons/react/24/outline";

import { QuoteContext } from "../contexts/QuoteContext";

export default function Bookmark({ news, deleteBookmark }) {
    const [open, setOpen] = useState(false);
    const { setQuote } = useContext(QuoteContext);
    
    const navigate = useNavigate();

    const handleOpenChange = () => setOpen(!open);

    const handleClickDelete = (e) => {
        // confirmation box
        if (window.confirm("Are you sure you want to delete this bookmark?")) {
            deleteBookmark(news.bookmark_id);
        }
    };

    const handleClickQuote = (e) => {
        setQuote(news);
        // go to chat page
        navigate("/chat");
    }
        

    return (
        <div className="bg-gray-700 rounded-lg p-3 mb-3">
            <div className="flex items-center justify-between ">
                <div className="text-l font-semibold">
                    <a
                        href={news.link}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {news.title}
                    </a>
                </div>
                <div className="flex text-right">
                    <AtSymbolIcon
                        className="h-5 w-5 mr-4 text-white hover:text-blue-300 cursor-pointer"
                        title="Quote in Chat"
                        onClick={handleClickQuote}
                    />
                    <TrashIcon
                        className="h-5 w-5 mr-4 text-white hover:text-blue-300 cursor-pointer"
                        title="Delete Bookmark"
                        onClick={handleClickDelete}
                    />
                    {open ? (
                        <ChevronUpIcon
                            onClick={() => handleOpenChange()}
                            className="h-5 w-5 text-white hover:text-blue-300 cursor-pointer"
                        />
                    ) : (
                        <ChevronDownIcon
                            onClick={() => handleOpenChange()}
                            className="h-5 w-5 text-white hover:text-blue-300 cursor-pointer"
                        />
                    )}
                </div>
            </div>
            {open ? (
                <div className="mt-3 text-normal font-normal">
                    {news.summary}
                </div>
            ) : null}
        </div>
    );
}
