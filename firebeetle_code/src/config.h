#ifndef CONFIG_H
#define CONFIG_H


// ESP-IDF headers
#include "driver/adc.h"
#include "esp_adc_cal.h"

// ESP-Arduino headers
#include "Arduino.h"
#include "AsyncUDP.h"
#include "SPIFFS.h"
#include "WiFi.h"
#include "Wire.h"

// claws/BH1750 Arduino library for digital light sensor BH1750
// https://github.com/claws/BH1750
#include "BH1750.h"


/**
 * Define whether to use serial output or not
 */
#define SERIAL_MONITOR 0


/**
 * Definition of voltage limits and sleep times
 */
#define WIFI_DOWN_VOLTAGE      3.3
#define STOP_MEASURING_VOLTAGE 2.9
#define BROWNOUT_VOLTAGE       2.8
#define SLEEP_SECONDS          300


/**
 * Definition of our Measurement Structure
 */
typedef struct measurement_t {
    float        voltage;
    float        old_voltage;
    float        cell_current;
    float        light;
    unsigned int measurement_count;
    unsigned int wifi_count;
    long int     timestamp;
    int          prediction;
} measurement_t;


/**
 * Definition ob buffer size for measurements
 */
#define MEASUREMENT_BUFFER_SIZE 1024


/**
 * Definition of ADC parameters and globals
 */
// multiplicative factor for Cap-Voltage measurement (Voltage Divider)
#define CAP_VOLT_FACTOR 2.0173
// resistance value in units Ohm
#define CELL_CURR_RESISTOR 985
// adc channels in use
#define CAP_VOLT_PIN  ADC1_CHANNEL_3
#define CELL_CURR_PIN ADC1_CHANNEL_0
// adc channel attenuation
#define CAP_VOLT_ATTEN  ADC_ATTEN_DB_11
#define CELL_CURR_ATTEN ADC_ATTEN_DB_0
// adc bit resolution
#define ADC_WIDTH ADC_WIDTH_BIT_10
// adc cycles to average over multiple measurements
#define ADC_CYCLES 32
// variables to store adc characteristics
extern esp_adc_cal_characteristics_t adc_cap_chars;
extern esp_adc_cal_characteristics_t adc_curr_chars;


/**
 * Definition of LightMeter parameters and globals
 */
#define LIGHTMETER_PIN GPIO_NUM_4
extern BH1750 lightMeter;


/**
 * Define Flash filename to store measurements
 */
#define FLASH_FILE "/buffer.bin"


/**
 * Declare WiFi globals
 */
extern const char* ssid;
extern const char* password;

extern const IPAddress local_ip;
extern const IPAddress gateway;
extern const IPAddress subnet;

extern const IPAddress server_ip;
extern const uint16_t  udp_port;
extern const uint16_t  tcp_port;


/**
 * Declare global persistent counters
 */
extern RTC_DATA_ATTR unsigned int boot_ctr;
extern RTC_DATA_ATTR unsigned int measure_ctr;
extern RTC_DATA_ATTR unsigned int wifi_ctr;
extern RTC_DATA_ATTR unsigned int flash_ctr;


/**
 * Declare functions
 */
void print_measurement(measurement_t* mmt);
void print_localtime(tm* local);
void print_localtime(time_t* tstmp);

void connect_wifi();
void disconnect_wifi();

void     config_adc();
uint32_t get_adc_value(adc1_channel_t pin);
float    get_cap_voltage();
float    get_cell_current();

void  config_luxmeter();
float get_lux();

time_t get_timestamp();

size_t send_tcp_package(uint8_t* buffer, size_t size);
size_t send_udp_package(uint8_t* buffer, size_t size);

void store_in_flash(uint8_t* buffer, size_t size);
void send_flash_to_tcp();
void list_flash_files(const char* directory = "/");

void goto_sleep();


#endif    // CONFIG_H
