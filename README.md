
# ProtonVPN Android Location Picker — GitHub build bootstrap

This repository bootstrap keeps the integration patch and GitHub Actions workflow. The workflow checks out the upstream ProtonVPN/android-app project, applies the picker patch, and attempts assembleProductionVanillaOpenSourceDebug. A successful run publishes the debug APK as a workflow artifact.

## Important status

- This is an unofficial community integration, not a Proton release.
- The picker accepts a two-letter ISO country code and routes the request through Proton's existing signed-in connection stack. Availability is subject to account plan and current server inventory.
- Build success and 32-bit ARM compatibility are not yet verified. Inspect the APK's lib/armeabi-v7a/ entries before assuming it supports 32-bit-only devices.
- The workflow uses the upstream master branch. Pin a reviewed upstream commit for reproducible builds before distributing APKs.

## Install into your GitHub repository

Upload these files into the root of ghostyx1337/ProtonVPN-LocationPicker-Android:

- .github/workflows/android-build.yml
- tools/integrate_picker.py
- README.md

Then open Actions → ProtonVPN Location Picker Android build → Run workflow. A push to main also starts it automatically.

If GitHub Actions fails, open the run logs; upstream SDK/NDK requirements or source drift may need adjustments.
