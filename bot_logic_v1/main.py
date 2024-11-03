from detection import Detection


def main():
    
    detection = Detection()
    # Initialize Bot
    print("Initializing completed!")
    # Wait for start key
    try:
        # Start Algorithm
        print("Algorithm started!")
        while True:
            pass

    except KeyboardInterrupt:
        detection.destroy()
        print("Exiting...")

if __name__ == "__main__":
    main()
