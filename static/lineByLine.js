let sentences = [];   // will be filled from fetch
const typingSpeed = 120;  // ms per character
const pauseBetween = 1200; // ms pause before next sentence
const output = document.getElementById("output");

let sentenceIndex = 0;
let charIndex = 0;
let caret;

function typeSentence() {
  if (sentences.length === 0) return; // nothing to type yet

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
        sentenceIndex = (sentenceIndex + 1); // loop safely
        typeSentence();
      }, 1000);
    }, pauseBetween);
  }
}

// listen for the array coming from fetch
document.addEventListener("ResultReady", (e) => {
  sentences = e.detail;   // update with array
  sentenceIndex = 0;
  charIndex = 0;
  typeSentence();
});
