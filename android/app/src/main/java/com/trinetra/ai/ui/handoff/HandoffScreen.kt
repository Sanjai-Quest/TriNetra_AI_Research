package com.trinetra.ai.ui.handoff

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.speech.RecognizerIntent
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HandoffScreen(viewModel: HandoffViewModel, onScanProductQr: () -> Unit = {}) {
    val context = LocalContext.current
    val state by viewModel.state.collectAsState()
    val liveLocation by viewModel.liveLocation.collectAsState()
    var sampleVoiceInput by remember { mutableStateOf("Box is intact, weight is normal, seal is intact") }
    var selectedCondition by remember { mutableStateOf("NORMAL") }
    var observedSerial by remember { mutableStateOf("") }
    var observedImei by remember { mutableStateOf("") }
    var backendHostField by remember {
        mutableStateOf(com.trinetra.ai.data.net.BackendConfig.getCustomHost(context))
    }

    val locationPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        if (permissions.values.any { it }) {
            viewModel.startLiveLocation()
        } else {
            Toast.makeText(context, "Location permission denied. GPS will be left empty.", Toast.LENGTH_LONG).show()
        }
    }

    LaunchedEffect(Unit) {
        val fineGranted = ContextCompat.checkSelfPermission(
            context, Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        val coarseGranted = ContextCompat.checkSelfPermission(
            context, Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
        if (!fineGranted && !coarseGranted) {
            locationPermissionLauncher.launch(
                arrayOf(Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION)
            )
        }
        viewModel.startLiveLocation()
    }

    // Speech Recognizer Intent Launcher
    val speechRecognizerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            val spokenMatches = result.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            val spokenText = spokenMatches?.firstOrNull()
            if (!spokenText.isNullOrBlank()) {
                sampleVoiceInput = spokenText
                viewModel.processIntent(HandoffIntent.ProcessVoiceInput(spokenText))
            } else {
                Toast.makeText(
                    context,
                    "Offline speech recognition is unavailable. Use a preset or type the transcript, then process it locally.",
                    Toast.LENGTH_LONG
                ).show()
            }
        } else {
            Toast.makeText(
                context,
                "Speech capture was unavailable offline. Use a preset or type the transcript for local parsing.",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    // Audio Permission Launcher
    val audioPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, "ta-IN")
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
                putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak voice testimony in Tamil or English...")
            }
            speechRecognizerLauncher.launch(intent)
        } else {
            Toast.makeText(context, "Microphone permission is required for voice activation.", Toast.LENGTH_SHORT).show()
        }
    }

    val triggerSpeechRecognition = {
        val hasMicPermission = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.RECORD_AUDIO
        ) == PackageManager.PERMISSION_GRANTED

        if (hasMicPermission) {
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-IN")
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_PREFERENCE, "ta-IN")
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
                putExtra(RecognizerIntent.EXTRA_PROMPT, "Speak voice testimony in Tamil or English...")
            }
            try {
                speechRecognizerLauncher.launch(intent)
            } catch (e: Exception) {
                Toast.makeText(context, "Speech recognition not available on this device: ${e.message}", Toast.LENGTH_LONG).show()
            }
        } else {
            audioPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("TriNetra: Doorstep Handoff", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Backend host override — set this to the laptop's current LAN IP before
            // going on stage. No rebuild required.
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF8E1))
            ) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("⚙️ Backend Host (edit before demo)", fontWeight = FontWeight.Bold, fontSize = 12.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        OutlinedTextField(
                            value = backendHostField,
                            onValueChange = { backendHostField = it },
                            placeholder = { Text("e.g. 192.168.1.50", fontSize = 12.sp) },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(onClick = {
                            com.trinetra.ai.data.net.BackendConfig.setCustomHost(context, backendHostField)
                            Toast.makeText(context, "Backend host saved", Toast.LENGTH_SHORT).show()
                        }) {
                            Text("Save", fontSize = 12.sp)
                        }
                    }
                }
            }

            // Checkpoint 1: Security Tamper Seal & GPS
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("1. Package Identification", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("PACKAGE IDENTIFIED", color = Color(0xFF008800), fontWeight = FontWeight.SemiBold)
                    Text("Order: ORD-98402 · Package: TRN-PKG-7729-A", fontWeight = FontWeight.Bold)
                    Text("Product: Smartphone · Expected: 642g", fontSize = 12.sp)
                    OutlinedTextField(
                        value = observedSerial,
                        onValueChange = { observedSerial = it },
                        label = { Text("Observed physical serial") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    OutlinedTextField(
                        value = observedImei,
                        onValueChange = { observedImei = it },
                        label = { Text("Observed IMEI") },
                        singleLine = true,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Button(
                        onClick = {
                            viewModel.processIntent(
                                HandoffIntent.SetPhysicalIdentity(observedSerial, observedImei)
                            )
                            Toast.makeText(context, "Physical identity captured", Toast.LENGTH_SHORT).show()
                        },
                        enabled = observedSerial.isNotBlank()
                    ) {
                        Text("Confirm physical identity")
                    }
                    Text(
                        liveLocation?.let { location ->
                            "GPS LIVE: ${String.format("%.6f", location.latitude)}, ${String.format("%.6f", location.longitude)}"
                        } ?: "GPS LIVE: Waiting for device location...",
                        fontSize = 12.sp,
                        color = if (liveLocation != null) Color(0xFF008800) else Color.Gray
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Button(onClick = onScanProductQr, modifier = Modifier.fillMaxWidth()) {
                        Text("SCAN PRODUCT QR")
                    }
                    // Condition selection
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        OutlinedButton(
                            onClick = { selectedCondition = "NORMAL" },
                            modifier = Modifier.weight(1f)
                        ) { Text("NORMAL", fontSize = 9.sp) }
                        OutlinedButton(
                            onClick = { selectedCondition = "DAMAGED" },
                            modifier = Modifier.weight(1f)
                        ) { Text("DAMAGED", fontSize = 9.sp) }
                        OutlinedButton(
                            onClick = { selectedCondition = "TAMPERED" },
                            modifier = Modifier.weight(1f)
                        ) { Text("TAMPERED", fontSize = 9.sp) }
                    }
                    // Submit button
                    Button(
                        onClick = { viewModel.processIntent(HandoffIntent.SubmitVerification(selectedCondition, null)) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Submit Verification")
                    }
                }
            }

            // Checkpoint 1.5: BLE Doorstep Scale Reading
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("1.5 DEMO GATT SCALE", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        "SIMULATED GATT PERIPHERAL · Dispatch baseline: 642g. Capture a telemetry reading.",
                        fontSize = 12.sp,
                        color = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        OutlinedButton(
                            onClick = { viewModel.processIntent(HandoffIntent.ScaleReading(642.0)) },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("⚖️ Consistent (642g)", fontSize = 11.sp)
                        }
                        OutlinedButton(
                            onClick = { viewModel.processIntent(HandoffIntent.ScaleReading(210.0)) },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("⚠️ Swap Detected (210g)", fontSize = 11.sp)
                        }
                    }
                    val reading = (state as? HandoffState.Success)?.scaleReading
                    if (reading != null) {
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "Captured: ${String.format("%.1f", reading.weightGrams)}g · HMAC ${reading.hmacSignature.take(12)}…",
                            fontSize = 11.sp,
                            fontFamily = FontFamily.Monospace,
                            color = Color(0xFF004488)
                        )
                    }
                }
            }

            // Checkpoint 2: Real Voice Activation
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text("2. Real-Time Voice Condition Intake", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(modifier = Modifier.height(10.dp))

                    // Primary Real-Time Microphone Button
                    Button(
                        onClick = { triggerSpeechRecognition() },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(54.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFD32F2F))
                    ) {
                        Text(
                            "🎙️ SPEAK VOICE TESTIMONY (LIVE MIC)",
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp
                        )
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    OutlinedTextField(
                        value = sampleVoiceInput,
                        onValueChange = { sampleVoiceInput = it },
                        label = { Text("Captured Voice Transcript") },
                        modifier = Modifier.fillMaxWidth()
                    )

                    Spacer(modifier = Modifier.height(10.dp))

                    Text("Quick Presets (or Speak via Mic above):", fontSize = 12.sp, color = Color.Gray)
                    Spacer(modifier = Modifier.height(4.dp))

                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        OutlinedButton(
                            onClick = {
                                sampleVoiceInput = "Box is intact, weight is normal, seal is intact"
                                viewModel.processIntent(HandoffIntent.ProcessVoiceInput(sampleVoiceInput))
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("Preset 1 (English)", fontSize = 9.sp)
                        }

                        OutlinedButton(
                            onClick = {
                                sampleVoiceInput = "Box damaged torn open weight empty"
                                viewModel.processIntent(HandoffIntent.ProcessVoiceInput(sampleVoiceInput))
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("Preset 2 (Torn)", fontSize = 9.sp)
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    val buttonColor by animateColorAsState(
                        targetValue = if (state is HandoffState.Recording) Color.Red else MaterialTheme.colorScheme.primary,
                        label = "RecordButtonAnimation"
                    )

                    Button(
                        onClick = {
                            viewModel.processIntent(HandoffIntent.ProcessVoiceInput(sampleVoiceInput))
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(46.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = buttonColor)
                    ) {
                        Text(
                            text = if (state is HandoffState.Recording) "PARSING AUDIO..." else "PROCESS TEXT TRANSCRIPT (NLP)",
                            fontWeight = FontWeight.Bold,
                            fontSize = 13.sp
                        )
                    }
                }
            }

            // Checkpoint 3: Dynamic State Rendering
            when (val s = state) {
                is HandoffState.Idle -> {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Box(modifier = Modifier.padding(16.dp)) {
                            Text("Tap 🎙️ SPEAK above to record live audio, or select a preset.", color = Color.Gray)
                        }
                    }
                }
                is HandoffState.Processing -> {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(24.dp))
                            Text(s.stageMessage, fontWeight = FontWeight.Medium)
                        }
                    }
                }
                is HandoffState.Success -> {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color(0xFFF0FFF0))
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("NLP PARSING SUCCESSFUL ✅", fontWeight = FontWeight.Bold, color = Color(0xFF006600))
                                Spacer(modifier = Modifier.weight(1f))
                                Text(
                                    if (s.engineUsed == "GROQ_CLOUD") "⚡ GROQ" else "💻 LOCAL",
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (s.engineUsed == "GROQ_CLOUD") Color(0xFF7B2FBE) else Color(0xFF555555)
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("${s.result.latencyMs} ms", fontSize = 12.sp, color = Color.Gray)
                            }

                            Divider(modifier = Modifier.padding(vertical = 8.dp))

                            Text("Anomaly Flag: ${if (s.result.anomalyDetected) "FLAGGED ⚠️" else "CLEAR ✅"}", fontWeight = FontWeight.Bold)
                            Text("Seal Status: ${s.result.sealIntegrityStatus}")
                            Text("Weight Assessment: ${s.result.weightAssessment}")
                            Text("Room SQLite Cache: QUEUED FOR WORKMANAGER SYNC 💾", fontSize = 12.sp, color = Color(0xFF004488))

                            Spacer(modifier = Modifier.height(8.dp))

                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .background(Color(0xFF222222), shape = RoundedCornerShape(6.dp))
                                    .padding(8.dp)
                            ) {
                                Text(
                                    s.telemetryJson,
                                    color = Color(0xFF00FF00),
                                    fontFamily = FontFamily.Monospace,
                                    fontSize = 10.sp
                                )
                            }
                            // Verdict display
                            s.decision?.let { decision ->
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    "Verdict: $decision",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                    color = Color(0xFF006600)
                                )
                            }
                        }
                    }
                }
                is HandoffState.Error -> {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer)
                    ) {
                        Text(
                            s.errorMessage,
                            color = MaterialTheme.colorScheme.onErrorContainer,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }
                else -> { /* other states */ }
            }
        }
    }
}
