/**
 * Cookie Consent Management
 */
(function() {
    'use strict';

    const COOKIE_CONSENT_KEY = 'cookie_consent';
    const COOKIE_EXPIRY_DAYS = 365;

    const cookieConsent = document.getElementById('cookie-consent');
    const acceptBtn = document.getElementById('cookie-accept');
    const declineBtn = document.getElementById('cookie-decline');

    /**
     * Set a cookie
     */
    const setCookie = (name, value, days) => {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = `expires=${date.toUTCString()}`;
        document.cookie = `${name}=${value};${expires};path=/;SameSite=Lax`;
    };

    /**
     * Get a cookie
     */
    const getCookie = (name) => {
        const nameEQ = name + '=';
        const ca = document.cookie.split(';');
        for (let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
        }
        return null;
    };

    /**
     * Show cookie consent banner
     */
    const showConsentBanner = () => {
        if (cookieConsent) {
            cookieConsent.style.display = 'block';
            setTimeout(() => {
                cookieConsent.classList.add('show');
            }, 100);
        }
    };

    /**
     * Hide cookie consent banner
     */
    const hideConsentBanner = () => {
        if (cookieConsent) {
            cookieConsent.classList.remove('show');
            setTimeout(() => {
                cookieConsent.style.display = 'none';
            }, 300);
        }
    };

    /**
     * Handle accept
     */
    const handleAccept = () => {
        setCookie(COOKIE_CONSENT_KEY, 'accepted', COOKIE_EXPIRY_DAYS);
        hideConsentBanner();
        // Enable analytics and ads here if needed
    };

    /**
     * Handle decline
     */
    const handleDecline = () => {
        setCookie(COOKIE_CONSENT_KEY, 'declined', COOKIE_EXPIRY_DAYS);
        hideConsentBanner();
        // Disable analytics and ads here if needed
    };

    /**
     * Initialize
     */
    const init = () => {
        const consent = getCookie(COOKIE_CONSENT_KEY);
        
        if (!consent) {
            showConsentBanner();
        }

        if (acceptBtn) {
            acceptBtn.addEventListener('click', handleAccept);
        }

        if (declineBtn) {
            declineBtn.addEventListener('click', handleDecline);
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

