import { useState, useContext, useEffect } from "react";
import {
    Accordion,
    AccordionHeader,
    AccordionBody,
} from "@material-tailwind/react";
import {
    BookmarkIcon as BookmarkIconFilled,
    ChevronDownIcon,
    ChevronUpIcon,
} from "@heroicons/react/24/solid";
import {
    BookmarkIcon,
    AtSymbolIcon,
} from "@heroicons/react/24/outline";

import { fetchData } from "../utils/fetchData";
import { UserContext } from "../contexts/UserContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";
import { QuoteContext } from "../contexts/QuoteContext";

function NewsCard({ news }) {
    const { userId } = useContext(UserContext);
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);
    const { setQuote } = useContext(QuoteContext);

    const [open, setOpen] = useState(false);
    const [bookmarked, setBookmarked] = useState(false);

    useEffect(() => {
        setBookmarked(news.bookmarked);
        
        console.log("news title", news.title, "bookmarked", news.bookmarked, "news id", news.id, "userId", userId, "currentWorkspace", currentWorkspace.id, "bookmarked", bookmarked);
    }, [news.bookmarked]);
    

    const handleOpenChange = () => setOpen(!open);

    const handleBookmarkChange = () => {
        console.log("bookmark news", news.title, news.id);

        // add bookmark
        const method = bookmarked ? "DELETE" : "POST";
        const url = `bookmark/${userId}/${currentWorkspace.id}/${news.id}`;
        
        fetchData(url, method);

        
        setBookmarked(!bookmarked);
    };

    const handleClickedLink = (e) => {
        console.log("Clicked link:", news.link);

        // send a post request to server sending news id and link
        const url = `click_article/${userId}/${currentWorkspace.id}/${news.id}`;
        fetchData(url, "POST");
    };

    const handleMention = (e) => {
        console.log("Mentioning news:", news.title);
        setQuote(news);
    };

    return (
        <div className="">
            <Accordion className="mb-1" open={open}>
                <AccordionHeader key={news.id} className="text-base border-gray-400 pt-2 pb-1 flex items-center">
                    <div className="flex-1 hover:text-blue-300 hover:underline cursor-pointer">
                        <a href={`${news.link}`} className="w-full" target="_blank" onClick={handleClickedLink}>
                            {news.title}
                        </a>
                    </div>
                    <div className="flex text-right">
                        <AtSymbolIcon
                            className="h-5 w-5 mr-4  hover:text-blue-300 cursor-pointer"
                            title="Mention"
                            onClick={handleMention}
                        />
                        {bookmarked ? (
                            <BookmarkIconFilled onClick={handleBookmarkChange} className="h-5 w-5 mr-4  hover:text-blue-300 cursor-pointer" />
                        ) : (
                            <BookmarkIcon onClick={handleBookmarkChange} className="h-5 w-5 mr-4  hover:text-blue-300 cursor-pointer" />
                        )}
                        {open ? (
                            <ChevronUpIcon
                                onClick={() => handleOpenChange()}
                                className="h-5 w-5 :text-blue-300 cursor-pointer"
                            />
                        ) : (
                            <ChevronDownIcon
                                onClick={() => handleOpenChange()}
                                className="h-5 w-5 hover:text-blue-300 cursor-pointer"
                            />
                        )}
                    </div>
                    
                </AccordionHeader>
                <AccordionBody className="text-gray-300 text-base pt-1 pb-2 ">
                    <div className="text-normal font-normal">{news.summary}</div>
                </AccordionBody>
            </Accordion>
        </div>
    );
}

export default NewsCard;
