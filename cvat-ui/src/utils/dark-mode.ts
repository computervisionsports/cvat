// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

const DARK_MODE_BODY_CLASS = 'cvat-dark-mode';

export function applyDarkModeClass(darkMode: boolean): void {
    if (darkMode) {
        document.body.classList.add(DARK_MODE_BODY_CLASS);
        document.documentElement.style.colorScheme = 'dark';
    } else {
        document.body.classList.remove(DARK_MODE_BODY_CLASS);
        document.documentElement.style.colorScheme = 'light';
    }
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
