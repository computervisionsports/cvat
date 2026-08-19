// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { Row, Col } from 'antd/lib/grid';
import Switch from 'antd/lib/switch';
import Text from 'antd/lib/typography/Text';

interface Props {
    darkMode: boolean;
    onSwitchDarkMode(enabled: boolean): void;
}

function AppearanceSettingsComponent(props: Props): JSX.Element {
    const { darkMode, onSwitchDarkMode } = props;

    return (
        <div className='cvat-appearance-settings'>
            <Row className='cvat-player-setting'>
                <Col span={24}>
                    <Switch
                        className='cvat-appearance-settings-dark-mode-switch'
                        checked={darkMode}
                        onChange={onSwitchDarkMode}
                    />
                    <Text className='cvat-text-color cvat-appearance-settings-dark-mode-label'>
                        Dark mode
                    </Text>
                </Col>
                <Col span={24}>
                    <Text type='secondary'>
                        Use a dark color scheme across the CVAT interface
                    </Text>
                </Col>
            </Row>
        </div>
    );
}

export default React.memo(AppearanceSettingsComponent);
