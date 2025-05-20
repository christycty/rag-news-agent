import { createContext, useState } from 'react';

const CurrentWorkspaceContext = createContext();

const CurrentWorkspaceContextProvider = ({ children }) => {
    const [currentWorkspace, setCurrentWorkspace] = useState(null);
    
    return (
      <CurrentWorkspaceContext.Provider value={{ currentWorkspace, setCurrentWorkspace }}>
          {children}
      </CurrentWorkspaceContext.Provider>
    )
  
  }
  
export { CurrentWorkspaceContextProvider, CurrentWorkspaceContext };