import { Link } from "react-router-dom";
import {
    Typography,
    List,
    ListItem,
    ListItemPrefix,
    Drawer,
    Card,
} from "@material-tailwind/react";
import {
    UserCircleIcon,
    Cog6ToothIcon,
    BookmarkIcon,
    ChatBubbleOvalLeftEllipsisIcon,
} from "@heroicons/react/24/solid";
import { NewspaperIcon } from "@heroicons/react/24/outline";

import SidebarProfile from "./SidebarProfile";

export default function Sidebar({ isDrawerOpen, setIsDrawerOpen }) {
    const closeDrawer = () => setIsDrawerOpen(false);

    return (
        <div>
            <Drawer
                open={isDrawerOpen}
                onClose={closeDrawer}
                size={250}
                overlay={false}
                className="bg-gray-900"
            >
                <Card
                    color="transparent"
                    shadow={false}
                    className="h-[calc(100vh)] p-2"
                >
                    {/* Top Icon and Title */}
                    <div className="mb-2 flex items-center gap-4 p-2 text-white">
                        {/* News Logo */}
                        <NewspaperIcon className="h-6 w-6" />
                        <Typography variant="h6">Little News Agent</Typography>
                    </div>
                    <List className="flex-grow overflow-y-auto text-white">
                        <Link to="/chat">
                            <ListItem>
                                <ListItemPrefix>
                                    <ChatBubbleOvalLeftEllipsisIcon className="h-5 w-5" />
                                </ListItemPrefix>
                                Chat
                            </ListItem>
                        </Link>
                        <Link to="/bookmark">
                            <ListItem>
                                <ListItemPrefix>
                                    <BookmarkIcon className="h-5 w-5" />
                                </ListItemPrefix>
                                Bookmark
                            </ListItem>
                        </Link>
                        <Link to="/configuration">
                            <ListItem>
                                <ListItemPrefix>
                                    <Cog6ToothIcon className="h-5 w-5" />
                                </ListItemPrefix>
                                Configuration
                            </ListItem>
                        </Link>
                        <Link to="/profile">
                            <ListItem>
                                <ListItemPrefix>
                                    <UserCircleIcon className="h-5 w-5" />
                                </ListItemPrefix>
                                Profile
                            </ListItem>
                        </Link>
                        {/* Separation Line */}
                        <hr className="my-2 border-blue-gray-50" />
                        {/* Chat History Area */}
                        {/* Title of Chat History */}
                        {/* <Typography variant="h6" color="blue-gray">
              Chat History
            </Typography>
            <div className="mt-2">
              <Input
                icon={<MagnifyingGlassIcon className="h-4 w-4" />}
                label="Search"
                color="teal"
                className=""
              />
            </div> */}
                    </List>
                    <SidebarProfile />
                </Card>
            </Drawer>
        </div>
    );
}
