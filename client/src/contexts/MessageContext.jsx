import { createContext, useState } from 'react';

const MessageContext = createContext();

const MessageContextProvider = ({ children }) => {
    const [message, setMessage] = useState("");
  
    return (
      <MessageContext.Provider value={{ message, setMessage }}>
          {children}
      </MessageContext.Provider>
    )
  
  }
  
export { MessageContextProvider, MessageContext };