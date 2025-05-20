import {
    BrowserRouter as Router,
    Routes,
    Route,
    Navigate,
} from "react-router-dom";

import { CurrentWorkspaceContextProvider } from "./contexts/CurrentWorkspaceContext";
import { WorkspaceContextProvider } from "./contexts/WorkspaceContext";
import { UserContextProvider } from "./contexts/UserContext";
import { QuoteContextProvider } from "./contexts/QuoteContext";

import useFetchUserData from "./utils/useFetchUserData";

import Chatpage from "./pages/Chatpage";
import BookmarkPage from "./pages/BookmarkPage";
import ConfigurationPage from "./pages/ConfigurationPage";
import ProfilePage from "./pages/ProfilePage";

const AppContent = () => {
    return (
        <div className="flex w-full">
            <Routes>
                <Route path="/" element={<Navigate to="/chat" />} />
                <Route path="/chat" element={<Chatpage />} />
                <Route path="/bookmark" element={<BookmarkPage />} />
                <Route path="/configuration" element={<ConfigurationPage />} />
                <Route path="/profile" element={<ProfilePage />} />
            </Routes>
        </div>
    );
};

const DataInitializer = () => {
    const { loading, error } = useFetchUserData();

    if (loading)
        return (
            <div className="flex items-center justify-center h-screen bg-gray-800 text-white">
                <div
                    className="w-10 h-10 border-4 border-t-4 border-gray-600 border-t-gray-700 rounded-full animate-spin"
                    role="status"
                    aria-label="Loading"
                ></div>
            </div>
        );
    if (error)
        return (
            <div className="flex items-center justify-center h-screen bg-gray-800 text-white">
                Error: {error}
            </div>
        );

    return <AppContent />;
};

export default function App() {
    return (
        <UserContextProvider>
            <WorkspaceContextProvider>
                <CurrentWorkspaceContextProvider>
                    <QuoteContextProvider>
                    <Router>
                        <DataInitializer />
                    </Router>
                    </QuoteContextProvider>
                </CurrentWorkspaceContextProvider>
            </WorkspaceContextProvider>
        </UserContextProvider>
    );
}
