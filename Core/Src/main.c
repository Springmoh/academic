#include "stm32f4xx.h"
#include <math.h>

uint32_t raw;
float voltage;
double integer, floating_n;

void gpio_config() {
	RCC->AHB1ENR |= 3;		// Enable GPIOA clock
	GPIOA->MODER &= ~(0b11111111111111111111111111111111); //clear all bits in register
	GPIOA->MODER |= (0b01010101010101010101010101010111); //set the pins to output mode
	GPIOB->MODER &= ~(0xFFFFFFFF); //clear all bits Port B
	GPIOB->MODER |= 0x55555555; //set the pins to output mode
}

int main() {
	gpio_config();  // Your existing GPIO config
	RCC->APB2ENR |= (1 << 8);  // Enable ADC1 clock
//	GPIOA->MODER |= (3 << 0);  // Set PA0 to analog mode (0b11)
	ADC->CCR &= ~(3 << 16);    // Clear prescaler bits
	ADC->CCR |= (2 << 16);     // Set prescaler to divide by 6
	ADC1->CR1 &= ~(1 << 24);   // 12-bit resolution
	ADC1->CR2 |= (1 << 10);    // EOC flag after each conversion
	ADC1->CR2 &= ~(1 << 11);   // Right-alignment of data
	ADC1->SQR3 = 0;            // Channel 0 (PA0) as first conversion
	ADC1->SQR1 &= ~(0xF << 20); // Sequence length = 1
	ADC1->CR2 |= (1 << 0);     // ADON = 1 (Enable ADC1)

	while (1) {
		ADC1->CR2 |= (1 << 30);           // Start ADC conversion

		while (!(ADC1->SR & (1 << 1))){

		}
		raw = ADC1->DR;             // Read ADC value (EOC clears automatically)

		voltage = (((float) raw / 4095.0) * 5.0 / 10.0 * 30.0) + 0.01;
		voltage = voltage > 10.0 ? 10.0 : voltage;
		floating_n = modf(voltage, &integer);

		switch ((int) integer) {
		case 0:
			GPIOA->ODR |= (0b0111111 << 1); //SET BIT HIGH
			GPIOA->ODR &= ~(0b1000000 << 1); //CLEAR THE OTHER BITS
			break;
		case 1:
			GPIOA->ODR |= (0b0000110 << 1);
			GPIOA->ODR &= ~(0b1111001 << 1);
			break;
		case 2:
			GPIOA->ODR |= (0b1011011 << 1);
			GPIOA->ODR &= ~(0b0100100 << 1);
			break;
		case 3:
			GPIOA->ODR |= (0b1001111 << 1);
			GPIOA->ODR &= ~(0b0110000 << 1);
			break;
		case 4:
			GPIOA->ODR |= (0b1100110 << 1);
			GPIOA->ODR &= ~(0b0011001 << 1);
			break;
		case 5:
			GPIOA->ODR |= (0b1101101 << 1);
			GPIOA->ODR &= ~(0b0010010 << 1);
			break;
		case 6:
			GPIOA->ODR |= (0b1111101 << 1);
			GPIOA->ODR &= ~(0b0000010 << 1);
			break;
		case 7:
			GPIOA->ODR |= (0b0000111 << 1);
			GPIOA->ODR &= ~(0b1111000 << 1);
			break;
		case 8:
			GPIOA->ODR |= (0b1111111 << 1);
			GPIOA->ODR &= ~(0b0000000 << 1);
			break;
		case 9:
			GPIOA->ODR |= (0b1101111 << 1);
			GPIOA->ODR &= ~(0b0010000 << 1);
			break;
		case 10:
			GPIOA->ODR |= (0b0111111 << 1);
			GPIOA->ODR &= ~(0b1000000 << 1);
			break;
		default:
			break;
		}

		switch ((int)(floating_n*10.0)) {
		case 0:
			GPIOA->ODR |= (0b00111111 << 8);
			GPIOA->ODR &= ~(0b11000000 << 8);
			break;
		case 1:
			GPIOA->ODR |= (0b00000110 << 8);
			GPIOA->ODR &= ~(0b11111001 << 8);
			break;
		case 2:
			GPIOA->ODR |= (0b10011011 << 8);
			GPIOA->ODR &= ~(0b01100100 << 8);
			break;
		case 3:
			GPIOA->ODR |= (0b10001111 << 8);
			GPIOA->ODR &= ~(0b01110000 << 8);
			break;
		case 4:
			GPIOA->ODR |= (0b10100110 << 8);
			GPIOA->ODR &= ~(0b01011001 << 8);
			break;
		case 5:
			GPIOA->ODR |= (0b10101101 << 8);
			GPIOA->ODR &= ~(0b01010010 << 8);
			break;
		case 6:
			GPIOA->ODR |= (0b10111101 << 8);
			GPIOA->ODR &= ~(0b01000010 << 8);
			break;
		case 7:
			GPIOA->ODR |= (0b00000111 << 8);
			GPIOA->ODR &= ~(0b11111000 << 8);
			break;
		case 8:
			GPIOA->ODR |= (0b10111111 << 8);
			GPIOA->ODR &= ~(0b01000000 << 8);
			break;
		case 9:
			GPIOA->ODR |= (0b10101111 << 8);
			GPIOA->ODR &= ~(0b01010000 << 8);
			break;
		default:
			GPIOA->ODR &= ~(0xff << 8);
			break;
		}

		if ((int) integer >= 10) {
			GPIOB->ODR |= (0b0000110 << 1);
			GPIOB->ODR &= ~(0b1111001 << 1);
		} else {
			GPIOB->ODR &= ~(0Xff);
		}
	}
}
