import { useState, useEffect } from "react";
import "./Carousel.css";

interface CarouselProps {
  images: string[];
  autoPlayInterval?: number;
}

export default function Carousel({
  images,
  autoPlayInterval = 3000,
}: CarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    }, autoPlayInterval);

    return () => clearInterval(interval);
  }, [images.length, autoPlayInterval]);

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  return (
    <div className="carousel">
      <div className="carousel-inner">
        <button
          className="carousel-button carousel-button-prev"
          onClick={goToPrevious}
          aria-label="Previous slide"
        >
          ‹
        </button>

        <div className="carousel-slides">
          {images.map((image, index) => (
            <div
              key={index}
              className={`carousel-slide ${
                index === currentIndex ? "active" : ""
              }`}
            >
              <img
                src={image}
                alt="Вазоактивный препарат"
                className="carousel-image"
              />
            </div>
          ))}
        </div>

        <button
          className="carousel-button carousel-button-next"
          onClick={goToNext}
          aria-label="Next slide"
        >
          ›
        </button>
      </div>
    </div>
  );
}
