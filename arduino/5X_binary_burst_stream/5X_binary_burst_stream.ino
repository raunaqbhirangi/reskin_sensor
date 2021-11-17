/*
  5X ReSkin Board Example Code
  By: Tess Hellebrekers
  Date: October 22, 2021
  License: This code is public domain but you buy me a beer if you use this and we meet someday (Beerware license).

  Library: Heavily based on original MLX90393 library from Theodore Yapo (https://github.com/tedyapo/arduino-MLX90393)
  Use this fork (https://github.com/tesshellebrekers/arduino-MLX90393) to access additional burst mode commands
  
  Read the XYZ magnetic flux fields and temperature across all five chips on the 5X ReSkin board
  Print binary data over serial port
*/

#include <Wire.h>
#include <MLX90393.h> 

#define Serial SERIAL_PORT_USBVIRTUAL

MLX90393 mlx0;
MLX90393 mlx1;
MLX90393 mlx2;
MLX90393 mlx3;
MLX90393 mlx4;

MLX90393::txyz data0 = {0,0,0,0}; //Create a structure, called data, of four floats (t, x, y, and z)
MLX90393::txyz data1 = {0,0,0,0};
MLX90393::txyz data2 = {0,0,0,0};
MLX90393::txyz data3 = {0,0,0,0};
MLX90393::txyz data4 = {0,0,0,0};

uint8_t mlx0_i2c = 0x0C; // these are the I2C addresses of the five chips that share one I2C bus
uint8_t mlx1_i2c = 0x13;
uint8_t mlx2_i2c = 0x12;
uint8_t mlx3_i2c = 0x10;
uint8_t mlx4_i2c = 0x11;

void setup()
{
  //Start serial port and wait until user opens it
  Serial.begin(115200);
  while (!Serial) {
    delay(5);
  }

  //Start default I2C bus for your board, set to fast mode (400kHz)
  Wire.begin();
  Wire.setClock(400000);
  delay(10);
  
  //start chips given address, -1 for no DRDY pin, and I2C bus object to use
  byte status = mlx0.begin(mlx0_i2c, -1, Wire);
  status = mlx1.begin(mlx1_i2c, -1, Wire);
  status = mlx2.begin(mlx2_i2c, -1, Wire);
  status = mlx3.begin(mlx3_i2c, -1, Wire);
  status = mlx4.begin(mlx4_i2c, -1, Wire);

  //default gain and digital filtering set up in the begin() function of library. Adjust here is you want to change them
  //mlx0.setGain(5); //accepts [0,7]
  //mlx0.setDigitalFiltering(5); // accepts [2,7]. refer to datasheet for hall configurations
  
  //Start burst mode for temp, x, y, and z for all chips
  //Burst mode: continuously sample temp, x, y, and z, at regular intervals without polling
  mlx0.startBurst(0xF);
  mlx1.startBurst(0xF);
  mlx2.startBurst(0xF);
  mlx3.startBurst(0xF);
  mlx4.startBurst(0xF);
}

void loop()
{
  //continuously read the most recent data from the data registers and save to data
  mlx0.readBurstData(data0); //Read the values from the sensor
  mlx1.readBurstData(data1); 
  mlx2.readBurstData(data2); 
  mlx3.readBurstData(data3); 
  mlx4.readBurstData(data4); 

  //write binary data over serial
  Serial.write((byte*)&data0, sizeof(data0));  
  Serial.write((byte*)&data1, sizeof(data1));  
  Serial.write((byte*)&data2, sizeof(data2));  
  Serial.write((byte*)&data3, sizeof(data3));  
  Serial.write((byte*)&data4, sizeof(data4));  
  Serial.println();

  //adjust delay to achieve desired sampling rate
  delayMicroseconds(500);

}
