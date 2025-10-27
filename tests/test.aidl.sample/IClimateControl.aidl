// Test fixture: AIDL interface for AIDL parser tests.
// Mirrors the ClimateControl example in input.yaml.

package com.example.vehicle;

interface IClimateControl {
    void setTemperature(in int zone, in float temperature, out boolean success);
    float getTemperature(in int zone);
    oneway void onTemperatureChanged(in int zone, in float newTemperature);
}
