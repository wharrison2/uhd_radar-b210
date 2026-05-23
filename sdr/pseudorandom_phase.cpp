#include <random>
#include "pseudorandom_phase.hpp"

using namespace std;


// Return a single float generated from random_generator (ch0)
float get_next_phase(bool transmit){
    if (transmit) {
        return (float) random_generator_tx();
    } else {
        return (float) random_generator_rx();
    }
}

// Return a single float for TX channel 1 phase dithering (independent sequence)
float get_next_phase_ch1(){
    return (float) random_generator_ch1();
}

// Return a vector of the next n phases
vector<float> get_next_n_phases(int n, bool transmit){
    vector<float> ph(n);
    for(int i=0;i<n;i++) {
        ph[i] = get_next_phase(transmit);
    }
    return ph;
}