/**
 * Phish Hunter AI — Content Script
 * Runs on all pages. Listens for messages from background
 * to get selected text if needed.
 */

// Listen for messages from background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'GET_SELECTION') {
        const selection = window.getSelection()?.toString().trim() || '';
        sendResponse({ selection });
    }
    // Return true to keep the message channel open for async sendResponse
    return true;
});
