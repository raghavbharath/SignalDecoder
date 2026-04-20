import serial
import struct
import time

# Simulation Constants
BAUD_RATE = 9600
SAMPLE_RATE = 100000  # 100kHz
SAMPLES_PER_BIT = int(SAMPLE_RATE / BAUD_RATE)

def get_uart_bits(byte: int) -> list[int]:
    """
    Returns a list of 10 bits: 1 Start (0), 8 Data (LSB first), 1 Stop (1)
    """
    bits = [] # Start bit (Logic Low)
    for i in range(7, -1, -1):
        # Extract bits LSB first
        bits.append((byte >> i) & 1)
    # bits.append(1) # Stop bit (Logic High)
    return bits

def generate_rle_pairs(bitstream):
    """
    Converts bits to [State, Duration] pairs.
    Maps bit 1 to Channel 1 (0x01) and bit 0 to 0x00.
    """
    pairs = []
    for bit in bitstream:
        # If bit is 1, state is 0x01 (Channel 1 High). 
        # If bit is 0, state is 0x00 (All Channels Low).
        state = 0x01 if bit == 1 else 0x00
        
        # In a real scenario, a single UART bit might be longer than 255 samples.
        # We handle RLE overflow by splitting into multiple pairs.
        count = SAMPLES_PER_BIT
        while count > 0:
            duration = min(count, 255)
            pairs.append([state, duration])
            count -= duration
    return pairs

def create_64_byte_packet(rle_pairs, seq):
    """
    Builds the 64-byte packet: [AA][BB][Seq][60 bytes Data][XOR]
    """
    header = b'\xAA\xBB'
    sequence = struct.pack('B', seq % 256)
    
    # Each pair is [State, Duration], so 30 pairs = 60 bytes
    data = bytearray()
    for p in rle_pairs[:30]: 
        data.append(p[0]) # The 8-bit channel state
        data.append(p[1]) # The duration (1-255)
    
    # Pad with zeros if we have fewer than 30 pairs to maintain 64-byte alignment
    while len(data) < 60:
        data.extend([0, 0])

    packet = header + sequence + data
    
    # Calculate XOR Checksum of the first 63 bytes
    checksum = 0
    for byte in packet:
        checksum ^= byte
    
    return packet + struct.pack('B', checksum)

if __name__ == "__main__":
    port_name = input('Enter the virtual port (e.g., /dev/ttyUSB0): ')
    try:
        ser = serial.Serial(port_name)
        print(f"[*] Simulation started on {port_name}...")
    except Exception as e:
        print(f"[!] Error opening port: {e}")
        exit(1)

    # "Hello World!\0" -> 0x48 0x65 0x6C 0x6C 0x6F 0x20 0x57 0x6F 0x72 0x6C 0x64 0x21 0x00
    message = b"Hello World!\x00"
    seq_num = 0

    try:
        while True:
            all_pairs = []
            for char_code in message:
                # 1. Convert char to UART bits
                bits = get_uart_bits(char_code)
                # 2. Convert bits to RLE pairs mapped to Channel 1
                all_pairs.extend(generate_rle_pairs(bits))
            
            # 3. Add an "Idle" period (Logic High on UART) between message loops
            # This makes it easier to see the start of the next 'H'
            all_pairs.extend([[0x01, 255], [0x01, 255]])

            # 4. Transmit in 64-byte USB-friendly chunks
            for i in range(0, len(all_pairs), 30):
                chunk = all_pairs[i : i + 30]
                packet = create_64_byte_packet(chunk, seq_num)
                ser.write(packet)
                seq_num += 1
                
            # Slow down the loop slightly to prevent flooding the virtual buffer
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n[*] Simulation stopped.")
        ser.close()
