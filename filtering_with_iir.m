%% FIR and IIR Filtering Comparison
clc; clear; close all;

%% Read audio file
[x, Fs] = audioread("C:\Users\cleme\Downloads\DSP_assignment\audioDSP.wav");

% Convert stereo to mono if needed
if size(x,2) == 2
    x = mean(x,2);
end

N = length(x);
t = (0:N-1)/Fs;

%% Plot original audio
figure;
plot(t, x);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original Audio Signal");
grid on;

%% ============================================================
%  1. FIR Filtering using conv()
% =============================================================

% FIR moving average filter
h = ones(1,10)/10;

% Apply FIR filter using conv()
y_fir_conv = conv(x, h, "same");

% Plot original vs FIR conv filtered signal
figure;
plot(t, x);
hold on;
plot(t, y_fir_conv);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original vs FIR Filtered Audio using conv()");
legend("Original", "FIR using conv()");
grid on;

% Frequency response of FIR filter
figure;
freqz(h, 1, 1024, Fs);
title("Frequency Response of FIR Filter using conv()");


%% ============================================================
%  2. FIR Filtering using filter()
% =============================================================

% FIR filter coefficients
b_fir = h;
a_fir = 1;

% Apply FIR filter using filter()
y_fir_filter = filter(b_fir, a_fir, x);

% Plot original vs FIR filter filtered signal
figure;
plot(t, x);
hold on;
plot(t, y_fir_filter);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original vs FIR Filtered Audio using filter()");
legend("Original", "FIR using filter()");
grid on;

% Frequency response of FIR filter
figure;
freqz(b_fir, a_fir, 1024, Fs);
title("Frequency Response of FIR Filter using filter()");


%% ============================================================
%  3. IIR Filtering using filter()
% =============================================================

% IIR Butterworth low-pass filter
fc = 1000;              % Cutoff frequency in Hz
Wn = fc/(Fs/2);         % Normalized cutoff frequency

[b_iir, a_iir] = butter(4, Wn, "low");

% Apply IIR filter using filter()
y_iir_filter = filter(b_iir, a_iir, x);

% Plot original vs IIR filtered signal
figure;
plot(t, x);
hold on;
plot(t, y_iir_filter);
xlabel("Time (s)");
ylabel("Amplitude");
title("Original vs IIR Filtered Audio using filter()");
legend("Original", "IIR using filter()");
grid on;

% Frequency response of IIR filter
figure;
freqz(b_iir, a_iir, 1024, Fs);
title("Frequency Response of IIR Filter using filter()");


%% ============================================================
%  4. Compare all filtered signals in time domain
% =============================================================

figure;
plot(t, x);
hold on;
plot(t, y_fir_conv);
plot(t, y_fir_filter);
plot(t, y_iir_filter);
xlabel("Time (s)");
ylabel("Amplitude");
title("Comparison of Original, FIR, and IIR Filtered Audio");
legend("Original", "FIR using conv()", "FIR using filter()", "IIR using filter()");
grid on;


%% ============================================================
%  5. Compare all filtered signals in frequency domain
% =============================================================

X = fft(x);
Y_fir_conv = fft(y_fir_conv);
Y_fir_filter = fft(y_fir_filter);
Y_iir_filter = fft(y_iir_filter);

f = (0:N-1)*(Fs/N);
halfN = floor(N/2);

figure;
plot(f(1:halfN), abs(X(1:halfN)));
hold on;
plot(f(1:halfN), abs(Y_fir_conv(1:halfN)));
plot(f(1:halfN), abs(Y_fir_filter(1:halfN)));
plot(f(1:halfN), abs(Y_iir_filter(1:halfN)));
xlabel("Frequency (Hz)");
ylabel("Magnitude");
title("Frequency Spectrum Comparison");
legend("Original", "FIR using conv()", "FIR using filter()", "IIR using filter()");
grid on;


%% ============================================================
%  6. Play audio one by one
% =============================================================

disp("Playing original audio...");
sound(x, Fs);
pause(length(x)/Fs + 1);

disp("Playing FIR using conv()...");
sound(y_fir_conv, Fs);
pause(length(x)/Fs + 1);

disp("Playing FIR using filter()...");
sound(y_fir_filter, Fs);
pause(length(x)/Fs + 1);

disp("Playing IIR using filter()...");
sound(y_iir_filter, Fs);