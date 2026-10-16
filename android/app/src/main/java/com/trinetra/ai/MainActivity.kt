package com.trinetra.ai

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Box
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Home
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.viewmodel.compose.viewModel
import android.widget.Toast
import com.trinetra.ai.ui.cv.CameraScreen
import com.trinetra.ai.ui.handoff.HandoffScreen
import com.trinetra.ai.ui.handoff.HandoffViewModel

@OptIn(ExperimentalMaterial3Api::class)
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                TriNetraApp()
            }
        }
    }
}

sealed class Screen(val route: String, val label: String, val icon: ImageVector) {
    object Handoff : Screen("handoff", "Handoff", Icons.Filled.Home)
    object Camera : Screen("camera", "CV Scan", Icons.Filled.Settings)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TriNetraApp() {
    val screens = listOf(Screen.Handoff, Screen.Camera)
    var selectedScreen by remember { mutableStateOf<Screen>(Screen.Handoff) }
    var scanProductQr by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val handoffViewModel: HandoffViewModel = viewModel()

    Scaffold(
        bottomBar = {
            NavigationBar {
                screens.forEach { screen ->
                    NavigationBarItem(
                        selected = selectedScreen == screen,
                        onClick = { selectedScreen = screen },
                        icon = { Icon(screen.icon, contentDescription = screen.label) },
                        label = { Text(screen.label) }
                    )
                }
            }
        }
    ) { innerPadding ->
        Box(modifier = Modifier.padding(innerPadding)) {
            when (selectedScreen) {
                is Screen.Handoff -> HandoffScreen(
                    viewModel = handoffViewModel,
                    onScanProductQr = {
                        scanProductQr = true
                        selectedScreen = Screen.Camera
                    }
                )
                is Screen.Camera -> CameraScreen(
                    onMetricsCaptured = handoffViewModel::updateCameraMetrics,
                    onPackageScanned = { orderId ->
                        if (handoffViewModel.updatePackageIdentifier(orderId)) {
                            scanProductQr = false
                            selectedScreen = Screen.Handoff
                            Toast.makeText(context, "Product identified: $orderId", Toast.LENGTH_SHORT).show()
                        }
                    },
                    onInvalidPackage = { value ->
                        Toast.makeText(context, "Invalid demo QR: $value. Scan ORD-98402.", Toast.LENGTH_SHORT).show()
                    },
                    scanProductQrOnly = scanProductQr,
                    onPhotoCaptured = handoffViewModel::updatePhotoPath
                )
            }
        }
    }
}
