
#!/usr/bin/env python3
"""Apply the Location Picker UI patch to a clean ProtonVPN/android-app checkout."""
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "project",
    nargs="?",
    default=".",
    help="path to ProtonVPN Android source checkout",
)
args = parser.parse_args()

ROOT = Path(args.project).resolve()
NAV = ROOT / "app/src/main/java/com/protonvpn/android/redesign/main_screen/ui/nav/MainNav.kt"
BAR = ROOT / "app/src/main/java/com/protonvpn/android/redesign/main_screen/ui/BottomBarView.kt"
STRINGS = ROOT / "app/src/main/res/values/strings.xml"

for path in (NAV, BAR, STRINGS):
    if not path.is_file():
        raise SystemExit(
            f"Not a ProtonVPN Android source checkout: missing {path}"
        )


def replace_once(path: Path, old: str, new: str):
    source = path.read_text(encoding="utf-8")
    count = source.count(old)

    if count != 1:
        raise SystemExit(
            f"Patch stopped: expected exactly one match in "
            f"{path.relative_to(ROOT)}; found {count}: {old[:90]!r}"
        )

    path.write_text(source.replace(old, new, 1), encoding="utf-8")


replace_once(
    NAV,
    "import androidx.activity.compose.LocalActivity\n",
    "import androidx.activity.compose.LocalActivity\n"
    "import androidx.compose.foundation.layout.Column\n"
    "import androidx.compose.foundation.layout.Spacer\n"
    "import androidx.compose.foundation.layout.height\n"
    "import androidx.compose.foundation.layout.padding\n"
    "import androidx.compose.foundation.layout.fillMaxWidth\n"
    "import androidx.compose.material3.Button\n"
    "import androidx.compose.material3.OutlinedTextField\n"
    "import androidx.compose.material3.Text\n"
    "import androidx.compose.runtime.mutableStateOf\n"
    "import androidx.compose.runtime.setValue\n"
    "import androidx.compose.ui.unit.dp\n",
)

replace_once(
    NAV,
    "import com.protonvpn.android.redesign.app.ui.MainActivityViewModel\n",
    "import com.protonvpn.android.redesign.app.ui.MainActivityViewModel\n"
    "import com.protonvpn.android.redesign.app.ui.MainActivity\n"
    "import com.protonvpn.android.redesign.CountryId\n"
    "import com.protonvpn.android.redesign.vpn.ConnectIntent\n"
    "import com.protonvpn.android.redesign.vpn.ServerFeature\n"
    "import com.protonvpn.android.vpn.ConnectTrigger\n",
)

replace_once(
    NAV,
    "enum class MainTarget {\n"
    "    Home, Countries, Gateways, Profiles, Settings;",
    "enum class MainTarget {\n"
    "    Home, Countries, Gateways, Profiles, Settings, LocationPicker;",
)

replace_once(
    NAV,
    "            SettingsScreen.route -> Settings\n",
    "            SettingsScreen.route -> Settings\n"
    "            LocationPickerScreen.route -> LocationPicker\n",
)

replace_once(
    NAV,
    "            MainTarget.Settings ->\n"
    "                navigateInternal(SettingsScreen, navOptions)\n",
    "            MainTarget.Settings ->\n"
    "                navigateInternal(SettingsScreen, navOptions)\n\n"
    "            MainTarget.LocationPicker ->\n"
    "                navigateInternal(LocationPickerScreen, navOptions)\n",
)

replace_once(
    NAV,
    "                    MainTarget.Settings -> settings(\n",
    "                    MainTarget.LocationPicker -> "
    "with(LocationPickerScreen) { locationPicker() }\n\n"
    "                    MainTarget.Settings -> settings(\n",
)

append = '''

/** Country-code picker that uses Proton's existing authenticated VPN connection stack. */
object LocationPickerScreen : ScreenNoArg<MainNav>("locationPicker") {
    @Composable
    private fun Content() {
        val activity = LocalActivity.current as MainActivity
        val activityViewModel: MainActivityViewModel =
            hiltViewModel(viewModelStoreOwner = activity)

        var countryCode by remember { mutableStateOf("JP") }
        var message by remember {
            mutableStateOf(
                "Choose a 2-letter country code, then connect with your signed-in Proton account."
            )
        }

        Column(Modifier.fillMaxSize().padding(24.dp)) {
            Text("Location picker")
            Spacer(Modifier.height(8.dp))
            Text(
                "Connect to the fastest available Proton VPN server in a chosen country. " +
                    "Availability depends on your plan and current server inventory."
            )
            Spacer(Modifier.height(20.dp))

            OutlinedTextField(
                value = countryCode,
                onValueChange = {
                    countryCode = it.filter { char -> char.isLetter() }
                        .uppercase().take(2)
                },
                label = { Text("Country code (e.g. JP, FR, US)") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )

            Spacer(Modifier.height(12.dp))

            Button(
                onClick = {
                    val code = countryCode.trim().uppercase()
                    if (code.length != 2 || !code.all { it in 'A'..'Z' }) {
                        message = "Enter a valid 2-letter country code."
                    } else {
                        val features =
                            EnumSet.noneOf(ServerFeature::class.java)

                        activityViewModel.connect(
                            activity.vpnActivityDelegate,
                            ConnectIntent.FastestInCountry(
                                CountryId(code),
                                features
                            ),
                            ConnectTrigger.CountriesCountry("location picker")
                        )

                        message =
                            "Connection requested for $code. Proton will select an available server for your account."
                    }
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Connect to country")
            }

            Spacer(Modifier.height(16.dp))
            Text(message)
        }
    }

    fun SafeNavGraphBuilder<MainNav>.locationPicker() =
        addToGraph(this) { Content() }
}
'''

if "object LocationPickerScreen :" in NAV.read_text(encoding="utf-8"):
    raise SystemExit(
        "Patch stopped: LocationPickerScreen already exists."
    )

with NAV.open("a", encoding="utf-8") as file:
    file.write(append)

replace_once(
    BAR,
    "    MainTarget.Settings -> R.string.botton_nav_settings\n",
    "    MainTarget.Settings -> R.string.botton_nav_settings\n"
    "    MainTarget.LocationPicker -> R.string.bottom_nav_location_picker\n",
)

replace_once(
    BAR,
    "    MainTarget.Settings ->\n"
    "        if (selected) CoreR.drawable.ic_proton_cog_wheel_filled "
    "else CoreR.drawable.ic_proton_cog_wheel\n",
    "    MainTarget.Settings ->\n"
    "        if (selected) CoreR.drawable.ic_proton_cog_wheel_filled "
    "else CoreR.drawable.ic_proton_cog_wheel\n"
    "    MainTarget.LocationPicker ->\n"
    "        if (selected) CoreR.drawable.ic_proton_earth_filled "
    "else CoreR.drawable.ic_proton_earth\n",
)

replace_once(
    STRINGS,
    '    <string name="bottom_nav_profiles">Profiles</string>\n',
    '    <string name="bottom_nav_profiles">Profiles</string>\n'
    '    <string name="bottom_nav_location_picker">Picker</string>\n',
)

print("Location Picker patch applied.")
