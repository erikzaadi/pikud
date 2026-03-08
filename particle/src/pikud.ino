/*
 * Red Alert Monitor - Particle Photon firmware
 *
 * Subscribes to the "alert_status" event published by the Raspberry Pi
 * (alerts.py) and drives the built-in RGB LED accordingly.
 *
 * The Pi handles all API polling and geo-blocked HTTPS - the Photon
 * just reacts to status changes pushed from the Pi via Particle cloud.
 *
 * ── LED colours ──────────────────────────────────────────────────────────────
 *   NO_ALERTS    off
 *   PRE_WARNING  pulsing yellow
 *   ALERT        pulsing red
 *   RESOLVED     pulsing blue  held for RESOLVED_DURATION_MS, then NO_ALERTS
 *
 * ── Library dependencies ─────────────────────────────────────────────────────
 *   none beyond Device OS
 */

// ---------------------------------------------------------------------------
// Timing
// ---------------------------------------------------------------------------

static const unsigned long RESOLVED_DURATION_MS = 300000; // 5 min

// ---------------------------------------------------------------------------
// LED colours  {R, G, B}
// ---------------------------------------------------------------------------

static const uint8_t COLOR_PRE_WARNING[3] = {255, 255, 0};  // yellow
static const uint8_t COLOR_ALERT[3]       = {255,   0, 0};  // red

static const unsigned long PULSE_PERIOD_MS = 2000;  // full blue pulse cycle

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

enum AlertStatus { NO_ALERTS, PRE_WARNING, ALERT, RESOLVED };
static const char* STATUS_NAMES[] = { "NO_ALERTS", "PRE_WARNING", "ALERT", "RESOLVED" };

static AlertStatus   currentStatus = NO_ALERTS;
static unsigned long resolvedSince = 0;

// Pending status from event handler - consumed by loop()
static AlertStatus pendingStatus    = NO_ALERTS;
static bool        hasPending       = false;

// Pending simulate command - set by cloud function, consumed by loop()
static char pendingSimCmd[32] = "";

// ---------------------------------------------------------------------------
// LED helpers
// ---------------------------------------------------------------------------

static void applyLed(AlertStatus s) {
    RGB.control(true);
    if (s == NO_ALERTS) RGB.color(0, 0, 0);
    // all active states are handled continuously in loop() via updatePulse()
}

// Smooth triangle-wave pulse: scales a base colour 0→100%→0 over PULSE_PERIOD_MS
static void updatePulse(uint8_t r, uint8_t g, uint8_t b) {
    unsigned long phase = millis() % PULSE_PERIOD_MS;
    uint8_t brightness = (phase < PULSE_PERIOD_MS / 2)
        ? (uint8_t)(phase * 255 / (PULSE_PERIOD_MS / 2))
        : (uint8_t)((PULSE_PERIOD_MS - phase) * 255 / (PULSE_PERIOD_MS / 2));
    RGB.color(
        (uint8_t)((uint16_t)r * brightness / 255),
        (uint8_t)((uint16_t)g * brightness / 255),
        (uint8_t)((uint16_t)b * brightness / 255)
    );
}

static void transitionTo(AlertStatus next) {
    if (next == currentStatus) return;
    currentStatus = next;
    applyLed(currentStatus);
    Serial.printlnf("[%lu] -> %s", millis(), STATUS_NAMES[currentStatus]);
}

// ---------------------------------------------------------------------------
// Event handler - called by Particle cloud on the system thread,
// so we only set a flag and let loop() do the work
// ---------------------------------------------------------------------------

void onAlertStatus(const char* event, const char* data) {
    if (!data) return;

    AlertStatus s = NO_ALERTS;
    if      (strcmp(data, "pre_warning") == 0) s = PRE_WARNING;
    else if (strcmp(data, "alert")       == 0) s = ALERT;
    else if (strcmp(data, "resolved")    == 0) s = RESOLVED;

    pendingStatus = s;
    hasPending    = true;
}

// ---------------------------------------------------------------------------
// Debug simulation
// ---------------------------------------------------------------------------

static void injectSimulation(const char* cmd) {
    if      (strcmp(cmd, "prewarning") == 0) { pendingStatus = PRE_WARNING; hasPending = true; }
    else if (strcmp(cmd, "alert")     == 0) { pendingStatus = ALERT;       hasPending = true; }
    else if (strcmp(cmd, "clear")     == 0) { pendingStatus = NO_ALERTS;   hasPending = true; }
    else if (strcmp(cmd, "resolved")  == 0) { pendingStatus = RESOLVED;    hasPending = true; }
    else Serial.printlnf("SIM: unknown '%s'", cmd);
}

static int simulateHandler(String cmd) {
    cmd.trim();
    strncpy(pendingSimCmd, cmd.c_str(), sizeof(pendingSimCmd) - 1);
    pendingSimCmd[sizeof(pendingSimCmd) - 1] = '\0';
    return 0;
}

static void handleSerial() {
    static char buf[32];
    static int  pos = 0;
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n' || c == '\r') {
            if (pos > 0) { buf[pos] = '\0'; pos = 0; injectSimulation(buf); }
        } else if (pos < (int)sizeof(buf) - 1) {
            buf[pos++] = c;
        }
    }
}

// ---------------------------------------------------------------------------
// Particle setup / loop
// ---------------------------------------------------------------------------

void setup() {
    Serial.begin(115200);

    // Take LED control early so we can show status during cloud connect
    RGB.control(true);
    RGB.color(0, 0, 30);  // dim blue while connecting

    // In non-threaded AUTOMATIC mode setup() blocks here until cloud is up
    waitUntil(Particle.connected);

    applyLed(NO_ALERTS);

    int reason = System.resetReason();
    Serial.printlnf("Reset reason: %d (%s)  free mem: %lu",
        reason,
        reason == RESET_REASON_WATCHDOG       ? "watchdog"    :
        reason == RESET_REASON_PANIC          ? "panic/fault" :
        reason == RESET_REASON_USER           ? "user"        :
        reason == RESET_REASON_UPDATE         ? "fw update"   :
        reason == RESET_REASON_POWER_DOWN     ? "power down"  :
        reason == RESET_REASON_POWER_BROWNOUT ? "brownout"    : "other",
        System.freeMemory());

    Particle.subscribe("alert_status", onAlertStatus, MY_DEVICES);
    Particle.function("simulate", simulateHandler);

    Serial.println("Waiting for alert_status events from Pi...");
    Serial.println("simulate: alert / immediate / clear / resolved");
}

void loop() {
    handleSerial();

    if (pendingSimCmd[0] != '\0') {
        char cmd[32];
        strncpy(cmd, pendingSimCmd, sizeof(cmd));
        pendingSimCmd[0] = '\0';
        injectSimulation(cmd);
    }

    // Apply any pending status update from the event handler
    if (hasPending) {
        hasPending = false;
        AlertStatus incoming = pendingStatus;

        if (incoming == RESOLVED) {
            // Pi sends RESOLVED explicitly - start the cooldown timer
            resolvedSince = millis();
            transitionTo(RESOLVED);
        } else {
            resolvedSince = 0;
            transitionTo(incoming);
        }
    }

    unsigned long now = millis();

    // RESOLVED cooldown expiry
    if (currentStatus == RESOLVED && (now - resolvedSince) >= RESOLVED_DURATION_MS) {
        resolvedSince = 0;
        transitionTo(NO_ALERTS);
    }

    // Continuous pulse for all active states
    switch (currentStatus) {
        case PRE_WARNING: updatePulse(COLOR_PRE_WARNING[0], COLOR_PRE_WARNING[1], 0);   break;
        case ALERT:       updatePulse(COLOR_ALERT[0],       0,                    0);   break;
        case RESOLVED:    updatePulse(0,                    0,                    255); break;
        default: break;
    }
}
