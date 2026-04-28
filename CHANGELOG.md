# Changelog for SignalDecoder

Put all SignalDecoder notes/changelog stuff here. Format adopted from [keepachangelog.com](https://keepachangelog.com).

```
## <date, or commit hash>

<notes>

### Added

### Changed

### Removed

## <older date/hash>
```
## 78fd5ad
- fixed the sequence tracking. Before it was tracking both the CAN and UART/SPI/I2C with the same sequence number, which caused dropped packet issues since seq numbers were being skipped CAN individually. Now added logic_seq and can_seq. 
- Also fixed the sequence drop calculation overflow. B4 it was going from 255 -> 1 but saying the differnece is -255, but now it correctly says the difference and is 255 -> 0. No longer false drops. 
- fixed the windows line endings in socat for WSL compatibility. 

Here's the transmitted packets from /tmp/ttyV0 - Virtual COM Port 0
[*] Sent CAN packet seq=0 id=0x123 (15 bytes)
[*] Sent logic packet seq=1 (516 bytes)
[*] Sent CAN packet seq=1 id=0x123 (15 bytes)
[*] Sent logic packet seq=2 (516 bytes)
[*] Sent CAN packet seq=2 id=0x123 (15 bytes)
[*] Sent logic packet seq=3 (516 bytes)

Here's the received packets from /tmp/ttyV1 - Virtual COM Port 1
2026/04/27 22:18:22 [parseLogicPacket]: Logic packet seq=27
2026/04/27 22:18:22 [parseCANPacket]: CAN packet seq=27 ID=0x123 DLC=8
2026/04/27 22:18:22 [parseLogicPacket]: Logic packet seq=28
2026/04/27 22:18:22 [parseCANPacket]: CAN packet seq=28 ID=0x123 DLC=8
2026/04/27 22:18:22 [parseLogicPacket]: Logic packet seq=29
2026/04/27 22:18:22 [parseCANPacket]: CAN packet seq=29 ID=0x123 DLC=8
2026/04/27 22:18:22 [parseLogicPacket]: Logic packet seq=30

## d7c4dc7

### Changed
- serial.go: I rewrote the ReadByteStream function to sync on 0xAABB/0xCCDD headers rather than 128-byte chunks - this was Arnav's idea. Added pending buffer for the packet spanning, ResetInputBuffer() when we open a port to flush out existing content, and also the done channel for duration-based stopping, and the Claude-generated DummyConn for testing it without Python. 
- Also added the Run() function which basically routes logic packets over to the eventual decoder that we build and CAN packets just straight to Python over TCP. 
- Added structs for LogicPackets and CANPackets. Also parseLogicPacket and parseCANPacket functions, and sequence drop detection. 
- Changed the bound checks in parse.go from >= 8 to >8, since there are 8 channels. 
- Commented out CAN from protocol switch and pins parsing since the bxCAN handles that. 
- In test.py, changed it a bit to generate correct 516-byte logic packets and variable-length CAN packets matching actual protocol. We actually don't use RLE encoding, even tho it was a great idea, so now it's raw sequential samples at 1MHz/115200 baud.

## ef28400d

### Changed

- **UPDATE:** The version in the last commit works. I'm just dumb and ran `go install` on an older version, and so the path variable was running the old version rather than the new version. The latest code works as expected.

## 53628d3

### Added

- All commit stuff from before included
- Added the initial code to get the CLI argument parsing and program configuration working.
- Added code for the `internal/serial` package, but it isn't reading the data off of the test python script just yet.
    - The Python script works. Running the `socat` script on ports `/dev/ttyUSB0` and `/dev/ttyUSB1` works, python script connects to the first port successfully, and `screen /dev/ttyUSB1 9600` successfully prints the random stuff onto the screen.
    - In the serial package code, I've added a logging print line which seemingly does not print. I do not know entirely why, but I'm assuming it is because of an overlooked portion of how goroutines function. 
- Once the serial code is complete, next comes the decoding, in `internal/decoder/<protocol name>`.
