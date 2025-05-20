import { createContext, useState } from 'react';

const UserContext = createContext();

const UserContextProvider = ({ children }) => {
    const [userId, setUserId] = useState("user123");
  
    return (
      <UserContext.Provider value={{ userId, setUserId }}>
          {children}
      </UserContext.Provider>
    )
  
  }
  
export { UserContextProvider, UserContext };