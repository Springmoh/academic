#include "stm32f4xx_hal.h"
#include "stm32f4xx.h"

// Lookup codes for seven-seg (common anode)
// Lookup codes for seven-seg (common anode)
#define SEG_S 		0x6D //0b01101101
#define SEG_K 		0x76 //0b01110110
#define SEG_E 		0x79 //0b01111001
#define SEG_desh	0b01000000
#define SEG_6		0b01111101
#define SEG_1		0b00000110
#define SEG_2		0b01011011

int dir = 1;

// Function Prototypes
void SystemClock_Config(void);

void GPIO_Init(void) { //pg 186 reference manual

// Enable GPIOA, GPIOB, GPIOC clock
	RCC->AHB1ENR = 0x07;
// PA0–PA2 as input and enable pulldown register
	GPIOA->MODER = 0;
	GPIOA->PUPDR = 0xAAAAAAAA;
// PB0–PB3 as output
	GPIOB->MODER = 0x0055;
// PC0–PC7 as output
	GPIOC->MODER = 0x5555;

}

void display_SKEE(void) {
	uint8_t skee[8] = { SEG_S, SEG_K, SEG_E, SEG_E, SEG_desh, SEG_6, SEG_1,
			SEG_2 };
	for (int i = 0; i < 8; i++) {
		GPIOC->ODR = skee[i];
		HAL_Delay(800);
	}
}

int main(void) {
	GPIO_Init();
	HAL_Init();

	while (1) {
		uint32_t sw0 = (GPIOA->IDR & (1 << 0));
		uint32_t sw1 = (GPIOA->IDR & (1 << 1));//
		uint32_t sw2 = (GPIOA->IDR & (1 << 4));

//		if(sw2){
//			GPIOB->ODR = 0b00001111;
//		}else{
//			GPIOB->ODR = 0b00000000;
//		}

		if (sw0 && !sw1 && !sw2) {
			GPIOB->ODR = 0x01;
			HAL_Delay(1000);
			GPIOB->ODR = 0x00;
			HAL_Delay(1000);
		} else if (sw1 && !sw0 && !sw2) {
			GPIOB->ODR = 0b00001100;
			HAL_Delay(400);
			GPIOB->ODR = 0b00000011;
			HAL_Delay(400);
		} else if (sw2 && !sw1 && !sw0) {
			uint8_t state;
			if(state <= 0){
				dir = 1;
			}else if (state >= 3){
				dir = -1;
			}
			state = state + dir;

			switch (state){
			case 0:
				GPIOB->ODR = 0b00000001;
				break;
			case 1:
				GPIOB->ODR = 0b00000010;
				break;
			case 2:
				GPIOB->ODR = 0b00000100;
				break;
			case 3:
				GPIOB->ODR = 0b00001000;
				break;
			}

			HAL_Delay(400);
		} else {
			GPIOB->ODR = 0x00;
			display_SKEE();
		}

	}
}
