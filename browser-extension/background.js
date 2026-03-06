/**
 * Phish Hunter AI — Extension Background Service Worker
 * Registers the right-click context menu.
 */

const MENU_ID = 'phish-hunter-analyze';

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: MENU_ID,
        title: '🔍 Analyze with Phish Hunter AI',
        contexts: ['selection', 'link', 'page'],
    });
    console.log('Phish Hunter AI: context menu registered.');
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId !== MENU_ID) return;

    let textToAnalyze = '';

    if (info.selectionText) {
        // User selected text
        textToAnalyze = info.selectionText;
    } else if (info.linkUrl) {
        // User right-clicked a link
        textToAnalyze = info.linkUrl;
    } else {
        // Whole page URL
        textToAnalyze = tab.url || '';
    }

    // Store the text so the popup can pick it up
    await chrome.storage.local.set({ pendingText: textToAnalyze });

    // Open the popup
    chrome.action.openPopup().catch(() => {
        // Fallback: just set the storage, user opens popup manually
    });
});
