from mux_tx_rx import SerialManager

def main():
    sm = SerialManager(simulate=True, name='A', debug=False)

    def on_receive(msg):
        try:
            vals = [float(v) for v in msg.split(',')]
        except Exception as e:
            print(f"[A RECEIVE ERROR] {e}")

    sm.on_receive = on_receive
    sm.start()

    try:
        while True:
            # Get 4 float values from user input
            user_input = input("Enter 4 floats separated by commas (val1,val2,val3,val4): ")
            try:
                vals = [float(v.strip()) for v in user_input.split(',')]
                if len(vals) != 4:
                    print("Please enter exactly 4 values.")
                    continue
            except ValueError:
                print("Invalid input. Please enter numbers only.")
                continue

            # Send formatted message
            msg = ','.join(f"{v:.1f}" for v in vals)
            sm.send(msg)
            print(f"[A SENT] {msg}")

    except KeyboardInterrupt:
        sm.stop()

if __name__ == "__main__":
    main()
