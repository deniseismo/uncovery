// frequently used elements
export const frequentElements = {
  gameFrame: document.querySelector('#game-frame'),
  playButton: document.querySelector('#play-button'),
  downloadButton: document.querySelector('#download-button'),
  textField: document.querySelector('#text-field'),
  selectOptions: document.querySelector('.select-options'),
  searchAndOptionsContainer: document.querySelector('.search-and-options-container'),
  activeButtonID() { return document.querySelector('.button.active').id }
};

/* a simple util function that insert an object after a reference object inside some parent container */
export function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
};

/* adds informational tooltips to their corresponding objects;
  used after for the winning message quotes; displays info about the quotes shown
*/
export function addTooltips() {
  const tooltippedElements = document.querySelectorAll('.info-tooltip')
  tooltippedElements.forEach((element) => {
    const tooltip = document.createElement('label');
    tooltip.classList.add('tooltipText');
    tooltip.textContent = element.dataset.tooltip;
    element.appendChild(tooltip);
  });
};