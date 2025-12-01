import React, { createContext, useContext, useEffect, useState } from "react";
import { getCartInfo, type CartInfo } from "./drugsApi";

type CartContextValue = {
  cart: CartInfo;
  refresh: () => Promise<CartInfo | undefined>;
  fetchOnPageEnter: () => Promise<CartInfo | undefined>;
  fetchOnClick: () => Promise<CartInfo | undefined>;
};

const CartContext = createContext<CartContextValue | undefined>(undefined);

export const CartProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [cart, setCart] = useState<CartInfo>({ order_id: 0, count: 0 });

  const fetch = async (): Promise<CartInfo | undefined> => {
    try {
      const info = await getCartInfo();
      setCart(info);
      return info;
    } catch (err) {
      // keep existing default on error
      return undefined;
    }
  };

  useEffect(() => {
    fetch();
  }, []);

  // Manage a single ongoing fetch to avoid duplicate requests.
  // currentFetch holds the active Promise when a request is in progress.
  // shouldLog marks whether we need to log the result once the fetch completes.
  let currentFetch: Promise<CartInfo | undefined> | null = null;
  let shouldLog = false;

  const doFetch = (log = false): Promise<CartInfo | undefined> => {
    // If a fetch is already in progress, record whether this caller
    // wants the result to be logged and return the same promise.
    if (currentFetch) {
      if (log) shouldLog = true;
      return currentFetch;
    }

    shouldLog = log;
    currentFetch = (async () => {
      try {
        const info = await getCartInfo();
        setCart(info);
        return info;
      } catch (err) {
        return undefined;
      }
    })();

    currentFetch.then((info) => {
      if (shouldLog) {
        try {
          console.log(`данные корзины:`, info);
        } catch (e) {
          /* noop */
        }
      }
      shouldLog = false;
      currentFetch = null;
    });

    return currentFetch;
  };

  const refresh = async () => {
    return await doFetch(false);
  };

  // Called when entering a page. This will log the cart data.
  const fetchOnPageEnter = async () => {
    return await doFetch(true);
  };

  // Called when user clicks the cart button. Don't log to avoid duplicate messages.
  const fetchOnClick = async () => {
    // Log on click as requested
    return await doFetch(true);
  };

  return <CartContext.Provider value={{ cart, refresh, fetchOnPageEnter, fetchOnClick }}>{children}</CartContext.Provider>;
};

export const useCart = (): CartContextValue => {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside CartProvider");
  return ctx;
};

export default CartContext;
