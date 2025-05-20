import { createContext, useState } from 'react';

const WorkspaceContext = createContext();

// a list of all workspace IDs of current user
const WorkspaceContextProvider = ({ children }) => {
    const [workspaces, setWorkspaces] = useState([]);
  
    return (
      <WorkspaceContext.Provider value={{ workspaces, setWorkspaces }}>
          {children}
      </WorkspaceContext.Provider>
    )
  
  }
  
export { WorkspaceContextProvider, WorkspaceContext };