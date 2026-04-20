import test  # Imports your test.py module
import os

def generate_to_file(filename, iterations=1):
    """
    Generates the bitstream packets and writes them to a binary file.
    """
    # Using the same message from the logic analyzer simulation
    message = b"Hello World!\x00"
    seq_num = 0
    
    # We use 'wb' mode for writing raw binary data
    with open(filename, 'wb') as f:
        print(f"[*] Generating {iterations} iteration(s) of the message...")
        
        for _ in range(iterations):
            all_pairs = []
            
            # Step 1: Use functions from test.py to create bitstream
            for char_code in message:
                bits = test.get_uart_bits(char_code)
                print(bits)
                # This uses the Channel 1 mapping (0x01) from your updated logic
                all_pairs.extend(test.generate_rle_pairs(bits))
            
            # Add the UART Idle period (Logic High / 0x01)
            all_pairs.extend([[0x01, 255], [0x01, 255]])
            
            # Step 2: Packetize into 64-byte chunks (30 pairs each)
            for i in range(0, len(all_pairs), 30):
                chunk = all_pairs[i : i + 30]
                packet = test.create_64_byte_packet(chunk, seq_num)
                
                # Write the raw 64-byte packet to the file
                f.write(packet)
                seq_num += 1

    print(f"[+] Done! Written to {filename} ({os.path.getsize(filename)} bytes)")

if __name__ == "__main__":
    output_file = "capture_test.bin"
    # Generating 1 iteration is usually enough for manual verification
    generate_to_file(output_file, iterations=1)
