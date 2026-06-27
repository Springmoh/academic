#ifndef SRC_PID_PID_H_
#define SRC_PID_PID_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdbool.h>
#include <stdarg.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

enum {TS = 0, SAT, KE, KU, KP, KI, KD, KN, B_0, B_1, C_1, D_0, D_1};

typedef struct{
	struct {
		unsigned s_flag	: 1;
	} flag;
	float *error;
	float *out_put;
	float K[13];
	float i_delay[2];
	float d_delay[2];
	float s_delay;
} PID_t;

void PIDSourceInit(float *in, float *out, PID_t *pid);
void PIDGainInit(float ts, float sat, float ke, float ku, float kp, float ki,
                 float kd, float kn, PID_t *pid);
void PIDGainSet(unsigned char a, float value, PID_t *pid);
void PIDCoeffCalc(PID_t *pid);
void PIDDelayInit(PID_t *pid);
char PIDIsSaturared(PID_t *pid);
void PID(PID_t *pid);

#ifdef __cplusplus
}
#endif

#endif