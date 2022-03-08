#include "config.h"


// reserve measurement buffer in persistent memory
RTC_DATA_ATTR uint8_t persistent_buffer[MEASUREMENT_BUFFER_SIZE];
// counter to track how many measurements are stored in persistent memory
RTC_DATA_ATTR uint8_t pb_ctr = 0;
// maximum number of measurements which can be stored in persistent memory
RTC_DATA_ATTR const uint8_t pb_max =
    MEASUREMENT_BUFFER_SIZE / sizeof(measurement_t);


float         vcap, icell, lux;
tm            local;
time_t        timestamp;
measurement_t measure_curr;
uint8_t*      measure_ptr = (uint8_t*) &measure_curr;

RTC_DATA_ATTR float old_volt = 0;


void setup() {
#if SERIAL_MONITOR
    Serial.begin(115200);
    Serial.println("\n<FireBeetle is ready>");
#endif

    // sleep timer in micro seconds
    esp_sleep_enable_timer_wakeup(SLEEP_SECONDS * 1000000);

    config_adc();
    config_luxmeter();

    if (boot_ctr == 0) {
        // start wifi on first boot to get time synchronization
        connect_wifi();

        // take initial measurement
        vcap  = get_cap_voltage();
        icell = get_cell_current();
        lux   = get_lux();
        getLocalTime(&local, 0);
        timestamp = mktime(&local);
        ++measure_ctr;

        measure_curr = (measurement_t){
            vcap, old_volt, icell, lux, measure_ctr, wifi_ctr, timestamp};

        // send initial measurement
        send_tcp_package(measure_ptr, sizeof(measurement_t));
        // and immediately disconnect
        disconnect_wifi();
    }
    ++boot_ctr;
}


void loop() {
    // measure capacitor voltage in V
    vcap = get_cap_voltage();
    // if voltage is below threshold --> STOP
    if (vcap < STOP_MEASURING_VOLTAGE) {
        goto_sleep();
    }

    // measure cell current in uA
    icell = get_cell_current();
    // measure illumination in lux
    lux = get_lux();
    // get current timestamp
    getLocalTime(&local, 0);
    timestamp = mktime(&local);
    // advance persistent measurement counter
    ++measure_ctr;

    // store current measurement as measurement_t struct
    measure_curr = (measurement_t){
        vcap, old_volt, icell, lux, measure_ctr, wifi_ctr, timestamp};

    print_localtime(&timestamp);
    print_measurement(&measure_curr);

    // store current measurement in persistent buffer
    if (pb_ctr < pb_max) {
        uint8_t* pb_ptr = persistent_buffer + pb_ctr * sizeof(measurement_t);
        memcpy(pb_ptr, measure_ptr, sizeof(measurement_t));
        pb_ctr++;
    }

    if (pb_ctr == pb_max) {
        if (vcap < WIFI_DOWN_VOLTAGE) {
            // store persistent buffer in flash
            store_in_flash(persistent_buffer, MEASUREMENT_BUFFER_SIZE);
        } else {
            connect_wifi();

            // send measurements stored in persistent buffer and flash memory
            send_tcp_package(persistent_buffer, MEASUREMENT_BUFFER_SIZE);
            send_flash_to_tcp();

            disconnect_wifi();
        }

        // reset persistent counter
        pb_ctr = 0;
    }


    // workload here


    // capture voltage right before shutdown
    old_volt = get_cap_voltage();
    // go into deep sleep mode
    goto_sleep();
    delay(1000);
}
