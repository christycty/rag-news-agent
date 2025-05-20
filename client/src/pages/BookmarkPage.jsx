import { useEffect, useContext, useState } from "react";
import { IconButton } from "@material-tailwind/react";
import { Squares2X2Icon, ListBulletIcon } from "@heroicons/react/24/solid";

import {
    XMarkIcon,
    Bars3Icon,
    ChevronLeftIcon,
    ChevronRightIcon,
} from "@heroicons/react/24/outline";

import { fetchData } from "../utils/fetchData";
import { deleteBookmark } from "../utils/api";

import Sidebar from "../components/Sidebar";
import Bookmark from "../components/Bookmark";

import { UserContext } from "../contexts/UserContext";
import { CurrentWorkspaceContext } from "../contexts/CurrentWorkspaceContext";

export default function BookmarkPage() {
    const { currentWorkspace } = useContext(CurrentWorkspaceContext);
    const { userId } = useContext(UserContext);

    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const openDrawer = () => setIsDrawerOpen(true);

    const pageSize = 10;
    const [bookmarks, setBookmarks] = useState([]);
    const [page, setPage] = useState(1);
    const [maxpage, setMaxpage] = useState(3); // temp

    // fetch bookmarks when component mounts
    useEffect(() => {
        fetchData(`bookmarks/${userId}/${currentWorkspace.id}`, "GET")
            .then((response) => {
                console.log("get bookmarks success, response:", response);
                setBookmarks(
                    response.map((bookmark) => ({
                        bookmark_id: bookmark.bookmark_id,
                        article_id: bookmark.article_id,
                        title: bookmark.metadata.title,
                        summary: bookmark.page_content,
                        link: bookmark.metadata.url,
                        timestamp: bookmark.metadata.fetch_date,
                        tags: bookmark.metadata.tags,
                        bookmarked: true,
                    }))
                );
                setMaxpage(Math.ceil(bookmarks.length / pageSize));
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    }, [userId, currentWorkspace]); // dependencies: userId and currentWorkspace

    const handleDeleteBookmark = (bookmark_id) => {
        console.log("Delete bookmark with id:", bookmark_id);
        deleteBookmark(bookmark_id)
            .then((response) => {
                console.log("Success:", response);
                setBookmarks(
                    bookmarks.filter((bookmark) => bookmark.bookmark_id !== bookmark_id)
                );
            })
            .catch((error) => {
                console.error("Error:", error);
            });
    };

    const incrementPage = () => {
        if (page === maxpage) setPage(1);
        else setPage(page + 1);
    };

    const decrementPage = () => {
        if (page === 1) setPage(maxpage);
        else setPage(page - 1);
    };

    return (
        <div className="flex w-full">
            <Sidebar
                isDrawerOpen={isDrawerOpen}
                setIsDrawerOpen={setIsDrawerOpen}
            />
            <div className="border-0 border-green-500 bg-gray-800 text-white h-screen w-full flex-col flex">
                {/* Hamburger icon for sidebar */}
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

                {/* Main content */}
                <div className="p-4 overflow-y-scroll">
                    {/* Header row of bookmark */}
                    <div className="flex items-center justify-between mb-4">
                        <div className="text-xl font-bold ">Bookmark </div>
                        <div className="flex items-center gap-2 hidden">
                            controls (view / page)
                            {/* Grid/List toggle */}
                            <div className="flex items-center gap-2 justify-center">
                                <Squares2X2Icon className="h-4 w-4" />
                                <ListBulletIcon className="h-4 w-4" />
                            </div>
                        </div>
                    </div>
                    {/* Bookmark list */}
                    <div>
                        {bookmarks
                            .slice((page - 1) * pageSize, page * pageSize)
                            .map((bookmark) => (
                                <Bookmark
                                    key={bookmark.bookmark_id}
                                    news={bookmark}
                                    deleteBookmark={handleDeleteBookmark}
                                />
                            ))}
                    </div>
                    <div className="mt-4 items-center justify-center flex gap-2">
                        <ChevronLeftIcon
                            className="h-4 w-4 hover:cursor-pointer"
                            onClick={decrementPage}
                        />
                        {page}
                        <ChevronRightIcon
                            className="h-4 w-4 hover:cursor-pointer"
                            onClick={incrementPage}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
