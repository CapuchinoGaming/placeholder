// Sentences can come from anywhere (API, user input, etc.)
const sentences = [
    "The sun dipped below the horizon.",
    "Shadows stretched across the field.",
    "A quiet calm settled over everything."
  ];
  // Settings
  const secondsPerChar = 0.05;   // typing speed per character
  const pauseBetween = 400;      // pause between sentences (ms)
  
  const output = document.getElementById("output");
  let i = 0;
  
  function showNext() {
    if (i >= sentences.length) return;  // stop when finished
  
    // Create a <p> dynamically
    const p = document.createElement("p");
    p.textContent = sentences[i];
    p.className = "typewriter";
  
    // Set CSS variables for this element
    const chars = sentences[i].length;
    const duration = Math.max(chars * secondsPerChar, 0.3);
    p.style.setProperty("--chars", chars);
    p.style.setProperty("--duration", `${duration}s`);
  
    // Add to DOM
    output.appendChild(p);

    // When typing animation ends, finalize and schedule next
    p.addEventListener("animationend", (e) => {
      if (e.animationName === "typing") {
        p.classList.remove("typewriter");
        p.classList.add("done");
        i++;
        

        setTimeout(showNext, pauseBetween);
      }
    });
  }
  
  // Start after DOM is ready
  document.addEventListener("DOMContentLoaded", showNext);
  