import { createContext, useState } from 'react';

const ServerIPContext = createContext();
const SERVER_IP = import.meta.env.VITE_SERVER_IP;

const ServerIPContextProvider = ({ children }) => {
    const [serverIP, setServerIP] = useState(SERVER_IP);
  
    return (
      <ServerIPContext.Provider value={{ serverIP }}>
          {children}
      </ServerIPContext.Provider>
    )
  
  }
  
export { ServerIPContextProvider, ServerIPContext };