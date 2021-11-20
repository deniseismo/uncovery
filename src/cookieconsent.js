export const cookieStorage = {
    getItem: (item) => {
        const cookies = document.cookie
            .split(';')
            .map(cookie => cookie.split('='))
            .reduce((acc, [key, value]) => ({ ...acc, [key.trim()]: value }), {});
        return cookies[item];
    },
    setItem: (item, value) => {
        document.cookie = `${item}=${value};`
    }
}

const storageType = cookieStorage;
const consentPropertyName = 'uncovery_cookie_consent';
const shouldShowPopup = () => !storageType.getItem(consentPropertyName);
const saveToStorage = () => storageType.setItem(consentPropertyName, true);

// display cookie consent message if the user's hasn't pressed 'accept' yet
export function handleCookieConsent() {

    const acceptFn = event => {
        // store it a cookie storage
        saveToStorage(storageType);
        consentPopup.classList.add('hidden');
    }
    const consentPopup = document.getElementById('consent-popup');
    const acceptBtn = document.getElementById('accept');
    // accept & store on click
    acceptBtn.addEventListener('click', acceptFn);

    if (shouldShowPopup(storageType)) {
        console.log('this triggered!')
        setTimeout(() => {
            consentPopup.classList.remove('hidden');
        }, 2000);
    }
};