import "./CartButton.css";
import { useCart } from "../CartContext";

interface CartButtonProps {
  orderId?: number; // kept for backward compatibility but unused
  count?: number;
}

export default function CartButton({ count }: CartButtonProps) {
  // Prefer props if provided, otherwise read from context
  const { cart, fetchOnClick } = useCart();
  const usedCount = count ?? cart.count;

  const handleClick = async () => {
    // Use the same centralized function as pages do
    try {
      await fetchOnClick();
    } catch (e) {
      // fail silently
    }
  };

  return (
    <div className="cart-footer">
      <a
        href="#"
        className="cart-icon-link"
        onClick={(e) => {
          e.preventDefault();
          void handleClick();
        }}
      >
        <div className="icon-circle">
          <span className="microscope">🔬</span>
          {usedCount > 0 && <span className="cart-badge">{usedCount}</span>}
        </div>
      </a>
    </div>
  );
}
