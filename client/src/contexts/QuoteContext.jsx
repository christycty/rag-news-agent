import { createContext, useState } from 'react';

const QuoteContext = createContext();

const QuoteContextProvider = ({ children }) => {
    const [quote, setQuote] = useState('');
  
    return (
      <QuoteContext.Provider value={{ quote, setQuote }}>
          {children}
      </QuoteContext.Provider>
    )
  
  }
  
export { QuoteContextProvider, QuoteContext };