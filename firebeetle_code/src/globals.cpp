#include "config.h"


/**
 * Initialize WiFi globals
 */
const char* ssid     = "Zombielab";
const char* password = "Tripod-2017";

const IPAddress local_ip(192, 168, 8, 112);
const IPAddress gateway(192, 168, 8, 1);
const IPAddress subnet(255, 255, 255, 0);

const IPAddress server_ip(192, 168, 8, 100);
const uint16_t  udp_port = 6819;
const uint16_t  tcp_port = 6819;


/**
 * Initialize ADC globals
 */
esp_adc_cal_characteristics_t adc_cap_chars;
esp_adc_cal_characteristics_t adc_curr_chars;


/**
 * Initialize lightMeter
 */
BH1750 lightMeter;


/**
 * Initialize persistent counters
 */
RTC_DATA_ATTR unsigned int boot_ctr    = 0;
RTC_DATA_ATTR unsigned int measure_ctr = 0;
RTC_DATA_ATTR unsigned int wifi_ctr    = 0;
RTC_DATA_ATTR unsigned int flash_ctr   = 0;
