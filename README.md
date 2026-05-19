# SignalDecoder


**Collaborators:** Raghav Bharathan (https://github.com/raghavbharath), Arnav Revankar (https://github.com/avr34)

The SignalDecoder is A Go-based serial packet decoder for the [ECE 692 USB Logic Analyzer][01] project at NJIT. Reads STM32 DMA-captured signal data over a serial port, decodes UART, SPI, I2C, and CAN protocols, and streams results to a Python PyQt6 GUI over TCP.

## Background

This is one component of a larger logic analyzer project built for ECE 692 (Embedded Systems). The STM32F446RE receiver board captures up to 8 digital channels simultaneously via DMA and streams packets to this decoder over serial. SignalDecoder handles packet parsing, protocol decoding, and forwarding results to the GUI over TCP.

## How It Works

Below is how data flows through this application:

- Data comes in from the STM32 via a serial port in a continuous stream. There are two packet types. Logic packets use header `0xAA 0xBB` and follow the format `[Header (2B)] [Sequence # (1B)] [512 samples (1B each)] [XOR checksum (1B)]` for a total of 516 bytes. Each sample byte encodes all 8 channels, where bit 0 = CH1 (PC0) through bit 7 = CH8 (PC7). CAN packets use header `0xCC 0xDD` and follow the format `[Header (2B)] [Sequence # (1B)] [ID_H] [ID_L] [DLC] [0-8 data bytes] [XOR checksum (1B)]` for a total of 7 to 15 bytes. CAN frames are pre-decoded by the STM32 bxCAN peripheral, so no raw CAN decoding happens here.
- The Go application is invoked by the Python GUI as a subprocess with several command line flags:
    - Which port to listen on (COM or /dev/tty\*)
    - Duration that the Go program should run for (capture period)
    - (Optional) Which protocol to decode: UART, SPI, I2C, or CAN
    - (Optional) Which channels to use for decoding (required if a protocol is specified):
        - For UART: `--pins tx=1,rx=2`
        - For SPI: `--pins miso=1,mosi=2,clk=3,cs=4`
        - For I2C: `--pins sda=1,scl=2`
        - For CAN: hardware-decoded on the STM32, no pin assignment needed
        - Where the numbers are the channel numbers (1 through 8)
        - Only one protocol can be decoded at a time
    - Once the Go program has run for the specified duration, it exits on its own and closes both the serial port and the TCP socket.
- Once invoked, the program listens to the port and does the following if decoding is enabled:
    - Reads incoming bytes off the serial port, syncs to a packet header (`0xAA 0xBB` or `0xCC 0xDD`), validates the XOR checksum, and parses the packet into an internal data format. This lives in `internal/serial/`.
    - The parsed packet is then passed to a goroutine that handles decoding, initialized with the correct protocol and channel settings. This lives in `internal/decoder/`.
    - The decoded output is then sent over a TCP socket to the Python GUI, which plots the waveform and overlays the decoded values (hex bytes, protocol fields) at the correct positions.

## Project Structure

```
SignalDecoder/
├── main.go                 # Entry point, orchestrates goroutines and channels
├── internal/
│   ├── serial/             # Serial port reading, packet sync, and framing
│   ├── decoder/            # Protocol decoding (UART, SPI, I2C, CAN)
│   ├── transport/          # TCP socket server to the Python GUI
│   └── config/             # Runtime configuration struct
├── go.mod
└── go.sum
```

## Packet Protocol Reference

| Type  | Header      | Format                                                       | Size       |
|-------|-------------|--------------------------------------------------------------|------------|
| Logic | `0xAA 0xBB` | `[seq (1B)][512 samples (1B each)][XOR checksum]`            | 516 bytes  |
| CAN   | `0xCC 0xDD` | `[seq (1B)][ID_H][ID_L][DLC][0-8 data bytes][XOR checksum]` | 7-15 bytes |

## Throughput Notes

- **USB CDC path**: 1MHz sample rate, the intended path for SPI and I2C decoding.
- **ST-Link USART path**: Practical ceiling of around 10kHz at 115200 baud. Only usable for UART at low baud rates.

## Credits

Raghav Bharathan and Arnav Revankar, as part of the ECE 692 USB Logic Analyzer project at NJIT.

<!-- Links -->
[01]: https://github.com/ragusauce4357/ECE692-Final-Project