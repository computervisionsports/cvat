// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

const DARK_MODE_BODY_CLASS = 'cvat-dark-mode';

export function applyDarkModeClass(darkMode: boolean): void {
    document.body.classList.toggle(DARK_MODE_BODY_CLASS, darkMode);
    document.documentElement.style.colorScheme = darkMode ? 'dark' : 'light';
    // Clears the pre-paint background set by the inline script in index.html once
    // the stylesheets own the page background.
    document.documentElement.style.backgroundColor = '';
}

export function readDarkModeFromStorage(): boolean {
    try {
        const settingsString = localStorage.getItem('clientSettings');
        if (!settingsString) {
            return false;
        }

        const loadedSettings = JSON.parse(settingsString);
        return loadedSettings.appearance?.darkMode === true;
    } catch {
        return false;
    }
}
