%% Read and listen to the audio
clc; clear; close all;

[x, Fs] = audioread("C:\Users\cleme\Downloads\DSP_assignment\audioDSP.wav");

%sound(x, Fs);   % Play original audio

%% Plot the original audio signal
N = length(x);
t = (0:N-1)/Fs;

figure;
plot(t, x);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original Audio Signal");
grid on;

%% Apply a simple FIR moving average filter using conv()
h = ones(1,10)/10;      % Moving average FIR filter

y_conv = conv(x, h, "same");

figure;
plot(t, x);
hold on;
plot(t, y_conv);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original vs Filtered Audio using conv()");
legend("Original", "Filtered");
grid on;

%sound(y_conv, Fs);      % Play filtered audio

%% Apply filtering using filter()
b = ones(1,10)/10;      % FIR numerator coefficients
a = 1;                  % FIR filter has no feedback

y_filter = filter(b, a, x);

figure;
plot(t, x);
hold on;
plot(t, y_filter);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original vs Filtered Audio using filter()");
legend("Original", "Filtered");
grid on;

sound(y_filter, Fs);

%% Check the filter frequency response using freqz()
figure;
freqz(b, a, 1024, Fs);
title("Frequency Response of the FIR Filter");


%% Compare original and filtered audio in frequency domain
X = fft(x);
Y = fft(y_filter);

f = (0:N-1)*(Fs/N);

figure;
plot(f(1:floor(N/2)), abs(X(1:floor(N/2))));
hold on;
plot(f(1:floor(N/2)), abs(Y(1:floor(N/2))));
xlabel("Frequency (Hz)");
ylabel("Magnitude");
title("Original vs Filtered Audio Spectrum");
legend("Original", "Filtered");
grid on;