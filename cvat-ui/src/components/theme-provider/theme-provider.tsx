// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React, { useEffect } from 'react';
import { useSelector } from 'react-redux';
import ConfigProvider from 'antd/lib/config-provider';
import { theme } from 'antd';

import { CombinedState } from 'reducers';
import { applyDarkModeClass } from 'utils/dark-mode';

interface Props {
    children: React.ReactNode;
}

function ThemeProvider(props: Props): JSX.Element {
    const { children } = props;
    const darkMode = useSelector((state: CombinedState) => state.settings.appearance.darkMode);

    useEffect(() => {
        applyDarkModeClass(darkMode);
    }, [darkMode]);

    return (
        <ConfigProvider
            theme={{
                algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
            }}
        >
            {children}
        </ConfigProvider>
    );
}

export default React.memo(ThemeProvider);
