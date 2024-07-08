/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontSize: {
        brand__font__size__xs: "12px",
        brand__font__size__sm: "14px",
        brand__font__size__base: "16px",
        brand__font__size__md: "20px",
        brand__font__size__lg: "24px",
        brand__font__size__xl: "52px",
        brand__font__size__2xl: "74px",
      },
      fontFamily: {
        brand__font__family__fancy: "El Messiri",
        brand__font__family__regular: "Karla",
      },
      fontWeight: {
        brand__font__light: "300",
        brand__font__regular: "400",
        brand__font__semibold: "600",
        brand__font__bold: "700",
      },
      screens: {
        xs: "300px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1536px",
      },
      colors: {
        primary: "#1976D2",
        secondary: "#1565c0",
        brand__white: "#FAF7F5",
        brand__cyan: "#007186",
        brand__light__cyan: "#08787F",
        brand__orange: "#EE6C4D",
        brand__warm__white: "#FFFAED",
        brand__sky__blue: "#D1E4F5",
        brand__navy__blue: "#002674",
        brand__dangerous: "#FF0000",
        brand__success: "#4BB543",
        brand__ash: "#FAFAFA",
        brand__ash__light: "#EBF0F4",
        brand__bg__hover: "#EEEEEE",
        brand__gray__border: "#ffffff4d",
        brand__detail__text: "rgb(75 85 99)",
        bg__gray: "rgba(255, 255, 255, 0.3)",
      },
      padding: {
        content__padding: "0 10px",
      },
      keyframes: {
        zoomIn: {
          "0%": {
            transform: "scale(1)",
          },
          "95%": {
            filter: "blur(0px)",
          },
          "100%": {
            filter: "blur(20px)",
            transform: "scale(1.5)",
          },
        },
        fadeIn: {
          "0%": {
            opacity: "0",
          },
          "100%": {
            opacity: "1",
          },
        },
        shimmer: {
          "100%": {
            transform: "translateX(100%)",
          },
        },
        arrowScrollDown: {
          "0%": {
            opacity: "0",
            transform: "translateY(-60px)",
          },
          "30%": {
            opacity: "1",
          },
          "100%": {
            opacity: "0",
            transform: "translateY(60px)",
          },
        },
      },
      animation: {
        zoom__in: "zoomIn 15s linear 1",
        fade__in: "fadeIn 0.35s ease-in 1",
        shimmer: "shimmer 1s ease-in infinite",
        arrow__scroll__down: "arrowScrollDown 2s infinite",
      },
      backgroundImage: {
        not__found: "url('../src/assets/svg/image-error-404.f7a6f4a6.svg')",
        landing__masking__title:
          "url('../src/assets/images/masking/text__clipping.jpg')",
        foreigner__background:
          "url('../src/assets/images/background/foreigner__bg.jpg')",
        popular__destination__background:
          "url('../src/assets/images/background/13237371_BG-6.jpg')",
        faq__background: "url('../src/assets/images/background/faq__bg.webp')",
        testimonial__background:
          "url('../src/assets/images/background/testimonial__bg.png')",
        photo__gallery__background:
          "url('../src/assets/images/background/photo__gallery.jpeg')",
        photo__gallery__background2:
          "url('../src/assets/images/background/photo__gallery__bg.webp')",
        ask__qus__background:
          "url('../src/assets/images/background/ask__qus__bg.jpeg')",
        footer__background:
          "url('../src/assets/images/background/footer__bg.jpg')",
        about__us__background:
          "url('../src/assets/images/background/about__us__bg.jpg')",
        sign__in__form__background:
          "url('../src/assets/images/background/sign__up__form__bg.jpg')",
        sign__up__form__background:
          "url('../src/assets/images/background/sign__in__form__bg.jpg')",
        pg__card__background:
          "url('../src/assets/images/background/pg__card__bg2.png')",
        checkbox__filter__bg:
          "url('data:image/svg+xml;base64,PHN2ZyBoZWlnaHQ9JzMwMHB4JyB3aWR0aD0nMzAwcHgnICBmaWxsPSIjZmZmZmZmIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgdmVyc2lvbj0iMS4xIiB4PSIwcHgiIHk9IjBweCI+PHRpdGxlPmljb25fYnlfUG9zaGx5YWtvdjEwPC90aXRsZT48ZGVzYz5DcmVhdGVkIHdpdGggU2tldGNoLjwvZGVzYz48ZyBzdHJva2U9Im5vbmUiIHN0cm9rZS13aWR0aD0iMSIgZmlsbD0ibm9uZSIgZmlsbC1ydWxlPSJldmVub2RkIj48ZyBmaWxsPSIjZmZmZmZmIj48ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgyNi4wMDAwMDAsIDI2LjAwMDAwMCkiPjxwYXRoIGQ9Ik0xNy45OTk5ODc4LDMyLjQgTDEwLjk5OTk4NzgsMjUuNCBDMTAuMjI2Nzg5MSwyNC42MjY4MDE0IDguOTczMTg2NDQsMjQuNjI2ODAxNCA4LjE5OTk4Nzc5LDI1LjQgTDguMTk5OTg3NzksMjUuNCBDNy40MjY3ODkxNCwyNi4xNzMxOTg2IDcuNDI2Nzg5MTQsMjcuNDI2ODAxNCA4LjE5OTk4Nzc5LDI4LjIgTDE2LjU4NTc3NDIsMzYuNTg1Nzg2NCBDMTcuMzY2ODIyOCwzNy4zNjY4MzUgMTguNjMzMTUyOCwzNy4zNjY4MzUgMTkuNDE0MjAxNCwzNi41ODU3ODY0IEw0MC41OTk5ODc4LDE1LjQgQzQxLjM3MzE4NjQsMTQuNjI2ODAxNCA0MS4zNzMxODY0LDEzLjM3MzE5ODYgNDAuNTk5OTg3OCwxMi42IEw0MC41OTk5ODc4LDEyLjYgQzM5LjgyNjc4OTEsMTEuODI2ODAxNCAzOC41NzMxODY0LDExLjgyNjgwMTQgMzcuNzk5OTg3OCwxMi42IEwxNy45OTk5ODc4LDMyLjQgWiI+PC9wYXRoPjwvZz48L2c+PC9nPjwvc3ZnPg==')",
      },
    },
  },
  plugins: [],
};

