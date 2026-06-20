const repoUrl = "https://github.com/risingsummit/deep-research-multi-agent";
const copyButton = document.querySelector("#copy-link");
const traceItems = [...document.querySelectorAll("#trace-list li")];

traceItems.forEach((item, index) => {
  item.style.transitionDelay = `${index * 80}ms`;
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
      }
    });
  },
  { threshold: 0.35 },
);

traceItems.forEach((item) => observer.observe(item));

copyButton?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(repoUrl);
    copyButton.textContent = "Copied";
  } catch {
    copyButton.textContent = "Repo link ready";
  }

  window.setTimeout(() => {
    copyButton.textContent = "Copy Repo Link";
  }, 1800);
});
