#include "config.h"


/**
 * Print aquired measurement on serial connection
 * @param  measurement_t* mmt  pointer to the measurement
 */
void print_measurement(measurement_t* mmt) {
#if SERIAL_MONITOR
    char str[128];
    // print measurement on serial port
    sprintf(str,
            "%.3f V, %.3f uA, %7.2f lux, %4d, %3d, %ld, %.3f V, pred: %-2d",
            mmt->voltage,
            mmt->cell_current,
            mmt->light,
            mmt->measurement_count,
            mmt->dhry_count,
            mmt->timestamp,
            mmt->old_voltage,
            mmt->prediction);
    Serial.println(str);
#endif
}


/**
 * Print the local time in human readable format
 * @param  tm* local  pointer to C Time structure
 */
void print_localtime(tm* local) {
#if SERIAL_MONITOR
    Serial.println(local, "%Y-%m-%dT%H:%M:%SZ");
#endif
}


/**
 * Print the local time in human readable format
 * @param  time_t* tstmp  pointer to C Time Type (UNIX timestamp)
 */
void print_localtime(time_t* tstmp) {
#if SERIAL_MONITOR
    print_localtime(localtime(tstmp));
#endif
}


/**
 * Establish WiFi connection
 */
void connect_wifi() {
#if SERIAL_MONITOR
    Serial.println("Establishing WiFi connection");
#endif

    WiFi.mode(WIFI_STA);
    WiFi.config(local_ip, gateway, subnet);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
#if SERIAL_MONITOR
        Serial.print(".");
#endif
        delay(100);
    }

#if SERIAL_MONITOR
    Serial.println("\nWiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
#endif

    // synchronize time (Timezone is UTC)
    configTime(0, 0, server_ip.toString().c_str());
    // force time update (timeout 3 seconds)
    tm local;
    getLocalTime(&local, 3000);

#if SERIAL_MONITOR
    Serial.println("Time synchronized");
    print_localtime(&local);
#endif

    // increase wifi connection counter
    ++wifi_ctr;
}


/**
 * Disconnect WiFi
 */
void disconnect_wifi() {
    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);

#if SERIAL_MONITOR
    Serial.println("WiFi disconnected");
#endif
}


/**
 * Configure and characterize ADC
 */
void config_adc() {
    // set adc bit resolution and channel attenuation
    adc1_config_width(ADC_WIDTH);
    adc1_config_channel_atten(CAP_VOLT_PIN, CAP_VOLT_ATTEN);
    adc1_config_channel_atten(CELL_CURR_PIN, CELL_CURR_ATTEN);
    // calibrate adc unit and save characteristics
    esp_adc_cal_characterize(
        ADC_UNIT_1, CAP_VOLT_ATTEN, ADC_WIDTH, 1100, &adc_cap_chars);
    esp_adc_cal_characterize(
        ADC_UNIT_1, CELL_CURR_ATTEN, ADC_WIDTH, 1100, &adc_curr_chars);
}


/**
 * Perform ADC measurement
 * @param  adc1_channel_t pin  the ADC input pin for the measurement
 * @return  uint32_t  raw ADC value averaged over ADC_CYCLES
 */
uint32_t get_adc_value(adc1_channel_t pin) {
    int adc_read = 0;

    // take adc measurement and average over ADC_CYCLES
    for (int i = 0; i < ADC_CYCLES; ++i) {
        adc_read += adc1_get_raw(pin);
    }

    return adc_read / ADC_CYCLES;
}


/**
 * Read ADC value on Cap-Voltage-Pin and translate into units V
 * @return float
 */
float get_cap_voltage() {
    int adc_read = get_adc_value(CAP_VOLT_PIN);
    // voltage in units mV
    int voltage = esp_adc_cal_raw_to_voltage(adc_read, &adc_cap_chars);
    // return capacitor voltage in units V
    return (float) voltage * CAP_VOLT_FACTOR / 1000;
}


/**
 * Read ADC value on Cell-Current-Pin and translate into units uA
 * @return float
 */
float get_cell_current() {
    int adc_read = get_adc_value(CELL_CURR_PIN);
    // voltage in units mV
    int voltage = esp_adc_cal_raw_to_voltage(adc_read, &adc_curr_chars);
    // return cell current in units uA
    return (float) voltage / CELL_CURR_RESISTOR * 1000;
}


/**
 * Configure and start lightMeter for measurements
 */
void config_luxmeter() {
    // power on lightMeter
    pinMode(LIGHTMETER_PIN, OUTPUT);
    digitalWrite(LIGHTMETER_PIN, HIGH);
    // start I2C bus and lightMeter
    Wire.begin();
    lightMeter.begin();
}


/**
 * Read lightMeter and return lux value
 * @return float
 */
float get_lux() {
    return lightMeter.readLightLevel();
}


/**
 * Get local time and return UNIX timestamp
 * @return time_t
 */
time_t get_timestamp() {
    tm local;
    getLocalTime(&local, 0);
    return mktime(&local);
}


/**
 * Send TCP package to server
 * @param  uint8_t* buffer  pointer to the send data
 * @param  size_t   size  size of the send data
 * @return  size_t  size of successfully sent data
 */
size_t send_tcp_package(uint8_t* buffer, size_t size) {
    WiFiClient tcp;

    if (!tcp.connect(server_ip, tcp_port)) {
#if SERIAL_MONITOR
        Serial.println("TCP connection failed.");
#endif
        return 0;
    }

    size_t sent = tcp.write(buffer, size);

#if SERIAL_MONITOR
    Serial.print("Bytes sent to server: ");
    Serial.println(sent);
#endif

    tcp.stop();

    return sent;
}


/**
 * Send UDP package to server
 * @param  uint8_t* buffer  pointer to the send data
 * @param  size_t   size  size of the send data
 * @return  size_t  size of successfully sent data
 */
size_t send_udp_package(uint8_t* buffer, size_t size) {
    AsyncUDP udp;

    if (!udp.connect(server_ip, udp_port)) {
#if SERIAL_MONITOR
        Serial.println("UDP connection failed");
#endif
        return 0;
    }

    size_t sent = udp.write(buffer, size);

#if SERIAL_MONITOR
    Serial.print("Bytes sent to server: ");
    Serial.println(sent);
#endif

    udp.close();

    return sent;
}


/**
 * Store measurements in flash memory
 */
void store_in_flash(uint8_t* buffer, size_t size) {
    SPIFFS.begin();

    // open file in binary append mode
    File file = SPIFFS.open(FLASH_FILE, "ab");
    // write persistenced buffer to flash
    file.write(buffer, size);
    file.close();
    ++flash_ctr;

#if SERIAL_MONITOR
    char str[64];
    sprintf(str, "Saved datasets in flash: %d", flash_ctr);
    Serial.println(str);
    sprintf(str, "Total SPIFFS flash used: %d kB", SPIFFS.usedBytes());
    Serial.println(str);
#endif
}


/**
 * Send measurements from flash memory to TCP
 */
void send_flash_to_tcp() {
    if (flash_ctr == 0) {
        return;
    }

#if SERIAL_MONITOR
    char str[64];
    sprintf(str, "Send %d datasets from flash to TCP", flash_ctr);
    Serial.println(str);
#endif

    SPIFFS.begin();
    uint8_t buffer[MEASUREMENT_BUFFER_SIZE];

    // open file in binary read mode
    File file = SPIFFS.open(FLASH_FILE, "rb");
    while (file.available()) {
        // send as many packagas as available
        file.read(buffer, MEASUREMENT_BUFFER_SIZE);
        send_tcp_package(buffer, MEASUREMENT_BUFFER_SIZE);
    }
    file.close();
    SPIFFS.remove(FLASH_FILE);
    flash_ctr = 0;
}


/**
 * List files stored in flash
 */
void list_flash_files(const char* directory) {
#if SERIAL_MONITOR
    Serial.print("Listing directory: ");
    Serial.println(directory);

    SPIFFS.begin();

    File root = SPIFFS.open(directory);
    if (!root) {
        Serial.println("- failed to open directory");
        return;
    }
    if (!root.isDirectory()) {
        Serial.println(" - not a directory");
        return;
    }

    File file = root.openNextFile();
    while (file) {
        if (file.isDirectory()) {
            Serial.print("  DIR : ");
            Serial.println(file.name());
            list_flash_files(file.name());
        } else {
            Serial.print("  FILE: ");
            Serial.print(file.name());
            Serial.print("\tSIZE: ");
            Serial.println(file.size());
        }
        file = root.openNextFile();
    }
#endif
}


/**
 * Turn off unnecessary peripherals and start deep sleep
 */
void goto_sleep() {
    digitalWrite(LIGHTMETER_PIN, LOW);
    adc_power_off();
    esp_deep_sleep_start();
}
