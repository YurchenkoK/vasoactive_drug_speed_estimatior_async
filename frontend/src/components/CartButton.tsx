import { useState } from "react";
import "./CartButton.css";

interface CartButtonProps {
  count?: number;
}

export default function CartButton({ count = 0 }: CartButtonProps) {
  const [cartCount] = useState(count);

  const handleClick = () => {
    console.log("Кнопка корзины нажата");
    return "0";
  };

  return (
    <div className="cart-footer">
      <a
        href="#"
        className="cart-icon-link"
        onClick={(e) => {
          e.preventDefault();
          handleClick();
        }}
      >
        <div className="icon-circle">
          <span className="microscope">🔬</span>
          {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}
        </div>
      </a>
    </div>
  );
}
