### Added

- Dark mode toggle in Settings > Appearance to switch the CVAT interface to a dark color scheme
  (<https://github.com/computervisionsports/cvat/pull/1>)

### Changed

- Theme colors are now exposed as CSS custom properties, so panels, text, borders and icons
  follow the selected color scheme instead of being pinned to the light palette
  (<https://github.com/computervisionsports/cvat/pull/1>)

- Toolbar and annotation icons are drawn with `currentColor`, so they inherit the surrounding
  text color and stay legible on both light and dark backgrounds
  (<https://github.com/computervisionsports/cvat/pull/1>)
