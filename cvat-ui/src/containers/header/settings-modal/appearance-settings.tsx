// Copyright (C) CVAT.ai Corporation
//
// SPDX-License-Identifier: MIT

import React from 'react';
import { connect } from 'react-redux';

import { switchDarkMode } from 'actions/settings-actions';
import { CombinedState } from 'reducers';
import AppearanceSettingsComponent from 'components/header/settings-modal/appearance-settings';

interface StateToProps {
    darkMode: boolean;
}

interface DispatchToProps {
    onSwitchDarkMode(enabled: boolean): void;
}

function mapStateToProps(state: CombinedState): StateToProps {
    return {
        darkMode: state.settings.appearance.darkMode,
    };
}

const mapDispatchToProps: DispatchToProps = {
    onSwitchDarkMode: switchDarkMode,
};

function AppearanceSettingsContainer(props: StateToProps & DispatchToProps): JSX.Element {
    return <AppearanceSettingsComponent {...props} />;
}

export default connect(mapStateToProps, mapDispatchToProps)(AppearanceSettingsContainer);
