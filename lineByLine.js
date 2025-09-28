const sentences = [
    "The sun dipped below the horizon.",
    "Shadows stretched across the field.",
    "A quiet calm settled over everything."
  ];
  
  const typingSpeed = 120;  // ms per character
  const pauseBetween = 1200; // ms pause before next sentence
  const output = document.getElementById("output");
  
  let sentenceIndex = 0;
  let charIndex = 0;
  let caret;
  
  function typeSentence() {
    // If starting a new sentence
    if (charIndex === 0) {
      output.textContent = ""; // clear old line
      caret = document.createElement("span");
      caret.className = "caret";
      output.appendChild(caret);
    }
  
    const current = sentences[sentenceIndex];
  
    if (charIndex < current.length) {
      caret.before(current[charIndex]); // insert char before caret
      charIndex++;
      setTimeout(typeSentence, typingSpeed);
    } else {
      // Done typing sentence
      setTimeout(() => {
        output.classList.add("fade-out");
  
        setTimeout(() => {
          output.classList.remove("fade-out");
          charIndex = 0;
          sentenceIndex = (sentenceIndex + 1);
          typeSentence();
        }, 1000); // wait for fade out
      }, pauseBetween);
    }
  }
  
  // Start typing after DOM is loaded
  document.addEventListener("DOMContentLoaded", typeSentence);
  