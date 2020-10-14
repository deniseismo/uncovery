// frequently used elements
export const frequentElements = {
  gameFrame: document.querySelector('#game-frame'),
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

export function removeAllChildNodes(parent) {
  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }
};

export function loadSpinner(node) {
  const spinner = document.createElement("img");
  const url = "static/images/loading/spinner-vinyl-64.gif";
  spinner.classList.add('spinner');
  spinner.src = url;
  node.appendChild(spinner);
};

export async function fetchAvatar(qualifier) {
  // fetches current tags list
  const response = await fetch('get_user_avatar', {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "qualifier": qualifier
    })
  });
  const avatar = await response.json();
  return avatar;
};

// fixes artist's/user's name as per last.fm correction
export function fixInputData(method, info) {
  if (method === 'by_artist' || method === 'by_username') {
    frequentElements.textField.value = info;
  };
};