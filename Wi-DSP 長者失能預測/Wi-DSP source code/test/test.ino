#include <bluefruit.h>
#define BUF_LENGTH          20
#define DEVICE_NAME       "GROUP5"
#define TICK_INTERVAL_us    2000
#define test_s_uuid 0xFF05
#define test_uuid 0xAA05


static uint8_t adc_value[BUF_LENGTH] = {0,};
static int counter = 0;
static bool connected2 = false;

BLEDis  bledis;    
BLEService        hs(test_s_uuid);
BLECharacteristic hsraw(test_uuid);

extern "C"
{
  void SysTick_Handler(void)
  {
     if (connected2){
      adc_value[counter] = analogRead(A5);
      counter++;
      if (counter >= BUF_LENGTH) {
        hsraw.notify(adc_value, BUF_LENGTH);
        counter = 0;
      }
    }
  }
} 

void setup()
{
  pinMode(LED_BUILTIN, OUTPUT);

  analogReadResolution(8);

  Bluefruit.configPrphBandwidth(BANDWIDTH_MAX);  
  Bluefruit.begin();
  Bluefruit.setName(DEVICE_NAME);
  Bluefruit.setTxPower(4);

  Bluefruit.Periph.setConnectCallback(connect_callback);
  Bluefruit.Periph.setDisconnectCallback(disconnect_callback);
  Bluefruit.Periph.setConnInterval(6, 12);

 
  bledis.setManufacturer("Yutech, Taiwan");
  bledis.setModel("TriAnswer");
  bledis.begin();

  hs.begin();

  hsraw.setProperties(CHR_PROPS_READ | CHR_PROPS_NOTIFY);
  hsraw.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS);
  hsraw.setMaxLen(BUF_LENGTH);
  hsraw.setFixedLen(BUF_LENGTH);
  hsraw.begin();
 
  startAdv();
  SysTick_Config( (F_CPU/1000000)*TICK_INTERVAL_us );
}

void startAdv(void)
{
 
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addTxPower();
  Bluefruit.Advertising.addService(hs);
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.setInterval(32, 244);   
  Bluefruit.Advertising.setFastTimeout(30);      
  Bluefruit.Advertising.start(0);                 
}

void loop()
{

}

void connect_callback(uint16_t conn_handle)
{
  BLEConnection* conn = Bluefruit.Connection(conn_handle);
  delay(1000);
  connected2 = true;
}

void disconnect_callback(uint16_t conn_handle, uint8_t reason)
{
  (void) conn_handle;
  (void) reason;
  connected2 = false;
}
