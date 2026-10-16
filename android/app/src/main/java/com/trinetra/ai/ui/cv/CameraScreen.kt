package com.trinetra.ai.ui.cv

import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.common.InputImage
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.trinetra.ai.cv.CVAnalysisResult
import com.trinetra.ai.cv.OpenCVProcessor
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import android.util.Log
import java.io.File
import com.trinetra.ai.identity.QrProductIdentifierSource
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/**
 * Extracts the Y (luma/grayscale) plane from a YUV_420_888 camera frame,
 * accounting for row stride so the buffer is a tightly packed width*height
 * grayscale array that OpenCVProcessor can consume directly.
 */
private fun ImageProxy.toGrayscaleBytes(): Triple<ByteArray, Int, Int> {
    val yPlane = planes[0]
    val rowStride = yPlane.rowStride
    val buffer = yPlane.buffer
    val w = width
    val h = height

    return if (rowStride == w) {
        val out = ByteArray(buffer.remaining())
        buffer.get(out)
        Triple(out, w, h)
    } else {
        // Row stride padding present (common on many devices) — copy row by row.
        val out = ByteArray(w * h)
        val rowBytes = ByteArray(rowStride)
        var offset = 0
        for (row in 0 until h) {
            buffer.get(rowBytes, 0, minOf(rowStride, buffer.remaining()))
            System.arraycopy(rowBytes, 0, out, offset, w)
            offset += w
        }
        Triple(out, w, h)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CameraScreen(
    onMetricsCaptured: (CVAnalysisResult) -> Unit = {},
    onPackageScanned: (String) -> Unit = {},
    onInvalidPackage: (String) -> Unit = {},
    scanProductQrOnly: Boolean = false,
    onPhotoCaptured: (String) -> Unit = {}
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val processor = remember { OpenCVProcessor() }
    val barcodeScanner = remember { BarcodeScanning.getClient() }
    val productIdentifierSource = remember { QrProductIdentifierSource() }
    var lastScannedValue by remember { mutableStateOf<String?>(null) }
    var currentMetrics by remember { mutableStateOf(CVAnalysisResult(0.28, 0.81, 42)) }

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission(),
        onResult = { granted ->
            hasCameraPermission = granted
        }
    )

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
    }

    // Throttle: only analyze a frame every ~400ms even though the camera delivers ~30fps,
    // so the CPU-bound math stays cheap and the on-screen numbers stay readable.
    val lastAnalysisMs = remember { AtomicLong(0L) }
    val analysisExecutor = remember { Executors.newSingleThreadExecutor() }
    val imageCaptureHolder = remember { mutableStateOf<ImageCapture?>(null) }

    DisposableEffect(Unit) {
        onDispose {
            analysisExecutor.shutdown()
            barcodeScanner.close()
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(if (scanProductQrOnly) "Scan Product QR" else "CameraX Real-Time Vision HUD", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            // Real CameraX Live Viewport
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(Color.Black),
                contentAlignment = Alignment.Center
            ) {
                if (hasCameraPermission) {
                    AndroidView(
                        factory = { ctx ->
                            val previewView = PreviewView(ctx).apply {
                                implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                                scaleType = PreviewView.ScaleType.FILL_CENTER
                            }
                            val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
                            cameraProviderFuture.addListener({
                                val cameraProvider = cameraProviderFuture.get()
                                val preview = Preview.Builder().build().also {
                                    it.setSurfaceProvider(previewView.surfaceProvider)
                                }
                                val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                                val imageCapture = ImageCapture.Builder()
                                    .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                                    .build()
                                imageCaptureHolder.value = imageCapture

                                // Real frame analysis: reads the actual Y-plane (grayscale) of

                                // each camera frame and runs it through OpenCVProcessor. This is
                                // what makes the on-screen wear metrics respond to what the lens
                                // is actually pointed at, instead of synthetic/random data.
                                val imageAnalysis = ImageAnalysis.Builder()
                                    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                                    .build()
                                    .also { analysis ->
                                        analysis.setAnalyzer(analysisExecutor) { imageProxy ->
                                            val now = System.currentTimeMillis()
                                            val last = lastAnalysisMs.get()
                                            if (now - last < 400) {
                                                // Throttle: skip this frame, still must close it.
                                                imageProxy.close()
                                                return@setAnalyzer
                                            }
                                            lastAnalysisMs.set(now)
                                            var barcodePending = false
                                            try {
                                                val (grayBytes, w, h) = imageProxy.toGrayscaleBytes()
                                                val result = processor.analyzeFrame(grayBytes, w, h)
                                                currentMetrics = result
                                                onMetricsCaptured(result)
                                                imageProxy.image?.let { mediaImage ->
                                                    barcodePending = true
                                                    barcodeScanner.process(
                                                        InputImage.fromMediaImage(mediaImage, imageProxy.imageInfo.rotationDegrees)
                                                    ).addOnSuccessListener { barcodes ->
                                                        barcodes.firstOrNull()?.rawValue?.let { rawValue ->
                                                            val normalized = rawValue.trim().uppercase()
                                                            if (normalized != lastScannedValue) {
                                                                lastScannedValue = normalized
                                                                val identifier = productIdentifierSource.resolve(normalized)
                                                                if (identifier != null) {
                                                                    onPackageScanned(identifier.orderId)
                                                                } else {
                                                                    onInvalidPackage(normalized)
                                                                }
                                                            }
                                                        }
                                                    }.addOnCompleteListener { imageProxy.close() }
                                                }
                                            } catch (e: Exception) {
                                                e.printStackTrace()
                                            } finally {
                                                if (!barcodePending) imageProxy.close()
                                            }
                                        }
                                    }

                                try {
                                    cameraProvider.unbindAll()
                                    cameraProvider.bindToLifecycle(
                                        lifecycleOwner,
                                        cameraSelector,
                                        preview,
                                        imageAnalysis,
                                        imageCapture
                                    )
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                }
                            }, ContextCompat.getMainExecutor(ctx))
                            previewView
                        },
                        modifier = Modifier.fillMaxSize()
                    )
                    // Capture Photo Button
                    Button(
                        onClick = {
                            val capture = imageCaptureHolder.value ?: return@Button
                            val photoFile = File(context.cacheDir, "evidence_${System.currentTimeMillis()}.jpg")
                            val outputOptions = ImageCapture.OutputFileOptions.Builder(photoFile).build()
                            capture.takePicture(
                                outputOptions,
                                ContextCompat.getMainExecutor(context),
                                object : ImageCapture.OnImageSavedCallback {
                                    override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                                        onPhotoCaptured(photoFile.absolutePath)
                                    }
                                    override fun onError(exception: ImageCaptureException) {
                                        Log.e("CameraScreen", "Photo capture failed: ${"$"}exception.message")
                                    }
                                }
                            )
                        },
                        modifier = Modifier.fillMaxWidth().wrapContentWidth(Alignment.CenterHorizontally)
                    ) {
                        Text("Capture Photo")
                    }

                    // Overlay HUD Target Box
                    Box(
                        modifier = Modifier
                            .size(180.dp)
                            .border(2.dp, Color(0xFF00FF66), RoundedCornerShape(8.dp))
                    )

                    // Telemetry Status Badge
                    Row(
                        modifier = Modifier
                            .align(Alignment.TopStart)
                            .padding(10.dp)
                            .background(Color(0xAA000000), RoundedCornerShape(6.dp))
                            .padding(horizontal = 8.dp, vertical = 4.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .background(Color.Green, RoundedCornerShape(4.dp))
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            "LIVE 30 FPS • BACK CAMERA",
                            color = Color.White,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            fontFamily = FontFamily.Monospace
                        )
                    }
                } else {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text("📷 Camera Permission Required", color = Color.White, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "TriNetra needs camera access to run live 30 FPS surface wear inspection.",
                            color = Color.LightGray,
                            fontSize = 12.sp
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = { permissionLauncher.launch(Manifest.permission.CAMERA) }) {
                            Text("Grant Camera Permission")
                        }
                    }
                }
            }

            // Live CV Metrics Display Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(if (scanProductQrOnly) "SCAN QR CONTAINING ORD-98402" else "LIVE PHYSICAL SIGNALS", fontWeight = FontWeight.Bold, fontSize = 15.sp)
                    Spacer(modifier = Modifier.height(10.dp))



                    Spacer(modifier = Modifier.height(6.dp))



                    Spacer(modifier = Modifier.height(6.dp))

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("Inference Latency:", fontWeight = FontWeight.Medium, fontSize = 13.sp)
                        Text("${currentMetrics.latencyMs} ms", fontFamily = FontFamily.Monospace, color = Color.Blue, fontSize = 13.sp)
                    }
                }
            }

            // Evidence interpretation stays deliberately non-diagnostic: these are physical signals,
            // not a validated counterfeit or wear classifier.
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE8F5E9)
                )
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text(
                        "EVIDENCE STATUS:",
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.Gray
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("PHYSICAL SIGNAL CAPTURED", fontWeight = FontWeight.Bold, color = Color(0xFF008800), fontSize = 16.sp)
                    Text("Telemetry data is being recorded to the active evidence case.", fontSize = 11.sp)
                }
            }
        }
    }
}
