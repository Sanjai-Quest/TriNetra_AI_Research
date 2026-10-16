package com.trinetra.ai.data.net

import android.content.Context

/**
 * Runtime-configurable backend host list.
 *
 * Previously the Spring Boot backend IP was hardcoded in three separate places
 * (HandoffViewModel, TelemetryUploadWorker) with no way to change it without a
 * rebuild. On demo day, if the venue WiFi assigns your laptop a different LAN
 * IP than whatever was hardcoded at build time, EVERY network call silently
 * fails after a multi-second timeout with no way to recover short of a rebuild.
 *
 * This stores an operator-editable "primary host" in SharedPreferences (set it
 * from the small field on the Handoff screen right before going on stage) and
 * tries it FIRST, falling back to the same sane defaults as before.
 */
object BackendConfig {
    private const val PREFS_NAME = "trinetra_backend_config"
    private const val KEY_CUSTOM_HOST = "custom_backend_host"

    private val DEFAULT_HOSTS = listOf(
        "http://127.0.0.1:8080"       // ADB reverse tunnel for a USB-connected device
    )

    fun getHosts(context: Context): List<String> {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val customHost = prefs.getString(KEY_CUSTOM_HOST, null)
        return if (!customHost.isNullOrBlank()) {
            listOf(normalize(customHost)) + DEFAULT_HOSTS
        } else {
            DEFAULT_HOSTS
        }
    }

    fun setCustomHost(context: Context, hostOrIp: String) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_CUSTOM_HOST, hostOrIp.trim()).apply()
    }

    fun getCustomHost(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(KEY_CUSTOM_HOST, "") ?: ""
    }

    /** Accepts "192.168.1.50" or "http://192.168.1.50:8080" and normalizes to the latter. */
    private fun normalize(input: String): String {
        val trimmed = input.trim()
        if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) return trimmed
        return "http://$trimmed:8080"
    }
}
