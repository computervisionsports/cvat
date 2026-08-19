// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import ConfigProvider from 'antd/lib/config-provider';
// Imported by path rather than from 'antd': babel-plugin-import rewrites named
// imports of the package root and does not produce a usable binding for `theme`.
import antdTheme from 'antd/lib/theme';

import { CombinedState } from 'reducers';
import { applyDarkModeClass } from 'utils/dark-mode';

interface Props {
    children: React.ReactNode;
}

// The dark algorithm dims secondary and disabled text far enough that captions
// and hints fall below a comfortable contrast ratio, so they are lifted here.
const DARK_TOKEN_OVERRIDES = {
    colorTextSecondary: 'rgba(255, 255, 255, 75%)',
    colorTextTertiary: 'rgba(255, 255, 255, 60%)',
    colorTextDescription: 'rgba(255, 255, 255, 60%)',
    colorTextDisabled: 'rgba(255, 255, 255, 40%)',
    colorTextPlaceholder: 'rgba(255, 255, 255, 40%)',
};

function ThemeProvider(props: Props): JSX.Element {
    const { children } = props;
    const darkMode = useSelector((state: CombinedState) => state.settings.appearance.darkMode);

    useEffect(() => {
        applyDarkModeClass(darkMode);
    }, [darkMode]);

    return (
        <ConfigProvider
            theme={{
                algorithm: darkMode ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
                token: darkMode ? DARK_TOKEN_OVERRIDES : {},
            }}
        >
            {children}
        </ConfigProvider>
    );
}

export default React.memo(ThemeProvider);
